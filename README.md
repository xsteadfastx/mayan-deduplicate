# mayan-deduplicate

** NO WARRANTY FOR ANYTHING!!! **

This is a little script to search for duplicates in [Mayan EDMS](http://mayan-edms.com/) and to delete them through their API. 

## Usage

The easiest way is to use the [docker image](). If you used the [recommended way to install Mayan EDMS](http://mayan-edms.com/download/), there should be a volume for the media named `mayan_media`. We use this volume in the run command.

```
$ docker run -v mayan_media:/var/lib/mayan xsteadfastx/mayan-deduplicate
```

It's also possible to add options already to the command:

```
$ docker run -v mayan_media:/var/lib/mayan xsteadfastx/mayan-deduplicate --username mayanadmin --password mayanpassword --url http://192.168.1.7:81
```

If this options are not given, it will asks for them in a prompt.
