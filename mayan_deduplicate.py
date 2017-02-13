import os.path

from collections import defaultdict

from hashlib import md5

import click

import pendulum

import requests
from requests.auth import HTTPBasicAuth


def get_document_list(url, username, password, path):
    """Get documents from mayan API.

    :param url: Mayan EDMS URL
    :param username: Mayan EDMS admin username
    :param password: Mayan EDMS admin password
    :param path: Path of Mayan media directory
    :type url: str
    :type username: str
    :type password: str
    :type path: str
    :returns: List with documents
    :rtype: list[dict]
    """
    docs = []
    api_url = f'{url}/api/documents/documents?json'

    while api_url:
        r = requests.get(
            api_url,
            auth=HTTPBasicAuth(
                username,
                password
            )
        )

        docs.extend(
            [
                {
                    'file': os.path.join(
                        path,
                        'document_storage',
                        i['latest_version']['file']
                    ),
                    'id': i['id'],
                    'date_added': i['date_added'],
                    'description': i['description'],
                    'document_type_label': i['document_type_label'],
                    'label': i['label'],
                }
                for i in r.json()['results']
            ]
        )

        api_url = r.json()['next']

    return docs


def get_sizes(documents):
    """Adds sizes to documents dict.

    :param documents: Document list
    :type documents: list[dict]
    :returns: Document list with added sizes
    :rtype: list[dict]
    """
    for i in documents:
        i['size'] = os.path.getsize(i['file'])

    return documents


def get_size_duplicates(documents_with_size):
    """Dict with size duplicates.

    :param documents_with_size: Document list with added sizes
    :type documents_with_size: list[dict]
    :returns: Dictionary with size duplicates
    :rtype: dict
    """
    sizes = defaultdict(list)

    for doc in documents_with_size:
        sizes[doc['size']].append(doc)

    # remove duplicates
    dupes = {}
    for k, v in sizes.items():
        if len(v) > 1:
            dupes[k] = v

    return dupes


def get_md5_duplicates(size_duplicates):
    """List of docs with same md5 sums.

    :param size_duplicates: Dictionary of size duplicates with size as key
    :type size_duplicates: dict
    :returns: List of MD5 duplicates
    :rtype: list[list[dict]]
    """
    md5s = []

    for size, docs in size_duplicates.items():

        # create md5 for the docs
        for i in docs:
            with open(i['file'], 'rb') as f:
                i['md5'] = md5(f.read()).hexdigest()

        # find duplicates in docs list
        dup_docs = []
        md5_list = [i['md5'] for i in docs]
        for i, j in enumerate(md5_list):
            if md5_list.count(j) >= 2:
                dup_docs.append(docs[i])

        if dup_docs:
            md5s.append(dup_docs)

    return md5s


def get_duplicates(url, username, password, path):
    """Get duplicates.

    :param url: Mayan EDMS URL
    :param username: Mayan EDMS admin username
    :param password: Mayan EDMS admin password
    :param path: Path of Mayan media directory
    :type url: str
    :type username: str
    :type password: str
    :type path: str
    :returns: List of MD5 duplicates
    :rtype: list[list[dict]]
    """
    click.echo('getting documents...')
    documents = get_document_list(url, username, password, path)

    click.echo('getting filesize duplicates...')
    documents_with_size = get_sizes(documents)
    size_duplicates = get_size_duplicates(documents_with_size)

    click.echo('getting MD5 duplicates...')
    md5_duplicates = get_md5_duplicates(size_duplicates)

    return md5_duplicates


def delete_document(url, username, password, id):
    """Delete item from Mayan EDMS.

    :param url: Mayan EDMS URL
    :param username: Mayan EDMS admin username
    :param password: Mayan EDMS admin password
    :param id: ID of Mayan document to delete
    :type url: str
    :type username: str
    :type password: str
    :type id: int
    :returns: True if deleted or False if not
    :rtype: bool
    """
    api_url = f'{url}/api/documents/documents/{id}?json'

    r = requests.delete(api_url, auth=HTTPBasicAuth(username, password))

    if r.status_code == 204:
        return True
    else:
        return False


def choose_from_list(lst):
    """A click interface for choosing from a list.

    :param lst: List of items
    :type lst: list
    :returns: Choosen item id
    :rtype: int
    """
    click.echo('\n')
    for pos, item in enumerate(lst):
        click.echo(
            '({pos}) {label} from {date} with id {id} and type {type}'.format(
                pos=pos,
                label=click.style(item['label'], fg='white'),
                date=click.style(
                    pendulum.from_format(
                        item['date_added'],
                        '%Y-%m-%dT%H:%M:%S.%fZ'
                    ).to_datetime_string(),
                    fg='cyan'
                ),
                id=click.style(str(item['id']), fg='blue'),
                type=click.style(item['document_type_label'], fg='cyan')
            )
        )

    return click.prompt('Item', type=int)


@click.command()
@click.option(
    '--username',
    prompt=True,
    envvar='USERNAME',
    help='Mayan username'
)
@click.option(
    '--password',
    prompt=True,
    envvar='PASSWORD',
    hide_input=True,
    help='Mayan password'
)
@click.option(
    '--url',
    prompt=True,
    envvar='URL',
    help='Mayan URL'
)
@click.option(
    '--path',
    type=click.Path(exists=True),
    prompt=True,
    envvar='DOCUMENT_PATH',
    help='Mayan media directory'
)
@click.version_option()
def ui(username, password, url, path):

    duplicates = get_duplicates(url, username, password, path)
    click.echo('found {} duplicates!'.format(len(duplicates)))
    click.echo('\nCHOOSE DOCUMENT TO KEEP\n')

    for dups in duplicates:
        id_to_keep = choose_from_list(dups)

        # delete keeper from list
        del dups[id_to_keep]

        for doc in dups:
            click.echo('delete {}...'.format(doc['id']))
            if delete_document(url, username, password, doc['id']):
                continue
            else:
                click.secho('there was a problem', fg='red')
