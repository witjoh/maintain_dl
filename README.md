# maintain_dl.py

This program maintains the mebers os a distribution list.

You must both give a configuration and distribution list file in the json format.

## dependencies

* https://github.com/Zimbra-Community/python-zimbra

## usage

usage: maintain_dl.py [-h] -c CONFIG -d DISTRIBUTION [-v]

    This utility maintains distributionlists using soap calls.
    It needs a config file and a distibution list file.  Both
    files needs to be in the JSON format.  The configuration file must
    at least have the following structure :

    {
      "url": "https://<YOUR ZIMBRA SERVER>:7071/service/admin/soap",
      "user": "admin@<YOUR DOMAIN>",
      "password": "<YOUR SECRET>"
    }

    The distribution list JSON format must be at least:

    {
      "name": "soap@koewacht.net",
      "id": "50cbb237-1342-427c-bc7e-f1f3533ce147",
      "members": [
        "member1@<YOUR DOMAIN>",
        "member2@<YOUR DOMAIN>"
      ]
    }

    Both files must be passed as arguments.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file in json format
  -d DISTRIBUTION, --distribution DISTRIBUTION
                        Distribution file in json format
  -v, --verbose         Turns verbose output on

## Note

* The id field in the distribution listis not used with this version.  
* Distribution lists are not created if non-existing, only members are maintained. 
