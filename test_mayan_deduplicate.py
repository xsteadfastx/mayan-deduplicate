from unittest import mock

import mayan_deduplicate

import pytest


@pytest.fixture
def config():
    return {
        'username': 'username',
        'password': 'password',
        'url': 'http://localhost:80',
        'path': '/tmp'
    }


@mock.patch('mayan_deduplicate.requests.get')
def test_get_document_list(mock_requests, config):

    mock_requests.return_value.json.return_value = {
        'count': 194,
        'next': False,
        'results': [
            {
                'id': 4,
                'latest_version': {
                    'file': '0af05143-b7d2',
                },
                'date_added': '2017-02-13T09:17:35.832975Z',
                'description': '',
                'document_type_label': 'Krankenrechnungen',
                'label': 'imgtopdf_generated_1202171043056.pdf',
            }
        ]
    }

    for i in mayan_deduplicate.get_document_list(
        config['url'],
        config['username'],
        config['password'],
        config['path']
    ):
        assert i == {
            'file': '/tmp/document_storage/0af05143-b7d2',
            'id': 4,
            'date_added': '2017-02-13T09:17:35.832975Z',
            'description': '',
            'document_type_label': 'Krankenrechnungen',
            'label': 'imgtopdf_generated_1202171043056.pdf',
        }


def test_get_sizes(config, tmpdir):
    tmpdir.join('foo.txt').write('foo')

    documents = [
        {
            'file': tmpdir.join('foo.txt').strpath,
            'id': 0
        }
    ]

    assert mayan_deduplicate.get_sizes(documents) == [
        {
            'file': tmpdir.join('foo.txt').strpath,
            'id': 0,
            'size': 3
        }
    ]


@pytest.mark.parametrize('input,expected', [
    (
        [
            {
                'file': 'aaa',
                'id': 0,
                'size': 3
            },
            {
                'file': 'bbb',
                'id': 1,
                'size': 3
            },
            {
                'file': 'ccc',
                'id': 2,
                'size': 4
            }
        ],
        {
            3: [
                {
                    'file': 'aaa',
                    'id': 0,
                    'size': 3
                },
                {
                    'file': 'bbb',
                    'id': 1,
                    'size': 3
                }
            ]
        }
    )
])
def test_get_size_duplicates(input, expected):

    assert mayan_deduplicate.get_size_duplicates(input) == expected


def test_get_md5_duplicates(config, tmpdir):
    tmpdir.join('foo0.txt').write('foo')
    tmpdir.join('foo1.txt').write('foo')
    tmpdir.join('foo2.txt').write('bar')
    tmpdir.join('bar0.txt').write('test')
    tmpdir.join('bar1.txt').write('test')

    size_duplicates = {
        3: [
            {
                'file': tmpdir.join('foo0.txt').strpath,
                'id': 0,
            },
            {
                'file': tmpdir.join('foo1.txt').strpath,
                'id': 1,
            },
            {
                'file': tmpdir.join('foo2.txt').strpath,
                'id': 2,
            },
        ],
        4: [
            {
                'file': tmpdir.join('bar0.txt').strpath,
                'id': 3,
            },
            {
                'file': tmpdir.join('bar1.txt').strpath,
                'id': 4,
            },
        ]
    }

    result = mayan_deduplicate.get_md5_duplicates(size_duplicates)

    id_list = []
    for i in result:
        id_list.append([j['id'] for j in i])

    assert id_list == [[0, 1], [3, 4]]
