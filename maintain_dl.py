#!/usr/bin/python
import argparse
import sys
import json
import pprint
import pythonzimbra.communication
from pythonzimbra.communication import Communication
import pythonzimbra.tools
from pythonzimbra.tools import auth
from pythonzimbra.tools import dict

def getOptions(args=sys.argv[1:]):
    prog_help = """
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
    """
    # Parse the command arguments and put them in an option object
    parser = argparse.ArgumentParser(description=prog_help, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-c", "--config", required=True,  help="Configuration file in json format")
    parser.add_argument("-d", "--distribution", required=True, help="Distribution file in json format")
    parser.add_argument("-v", "--verbose", action='store_true', help="Turns verbose output on")
    options = parser.parse_args(args)
    return options

def readJson(jsonfile):
    with open (jsonfile) as jf:
        try:
            return json.load(jf)
        except Exception as e:
            print(repr(e))
            sys.exit(1)

def getToken(url, user, password):
    usr_token = auth.authenticate(
        url,
        user,
        password,
        admin_auth = True,
        use_password = True,
    )
    return usr_token

def getDlData(name, url, token):
    comm = Communication(url)
    info_request = comm.gen_request(token=token)
    info_request.add_request(
        'GetDistributionListRequest',
        {
             'dl': {
             '_content': name,
             'by': 'name'
            }
         },
         'urn:zimbraAdmin'
    )
    info_response = comm.send_request(info_request)
    data = {}
    data['members'] = []
    if not info_response.is_fault():
        zimbra_data = info_response.get_response()['GetDistributionListResponse']
        data['settings'] = dict.zimbra_to_python(zimbra_data['dl']['a'],
                                                 key_attribute='n',
                                                 content_attribute='_content')
        if 'dlm' in zimbra_data['dl']:
            for i in zimbra_data['dl']['dlm']:
                data['members'].append(i['_content'])

        data['id'] = zimbra_data['dl']['id']
        data['name'] = zimbra_data['dl']['name']
        return data
    else:
        print(info_response.get_fault_message())
        sys.exit(1)

def addMembers(dlId, member, url, token):
    if options.verbose:
        print('adding member: ', member)
    comm = Communication(url)
    info_request = comm.gen_request(token=token)
    info_request.add_request(
        'AddDistributionListMemberRequest',
        {
            'id': dlId,
            'dlm': {
                '_content': member
            }
         },
         'urn:zimbraAdmin'
    )
    info_response = comm.send_request(info_request)
    if not info_response.is_fault():
        zimbra_data = info_response.get_response()['AddDistributionListMemberResponse']
    else:
        print(info_response.get_fault_message())
        sys.exit(1)

def delMembers(dlId, member, url, token):
    if options.verbose:
        print('deleting member: ', member)
    comm = Communication(url)
    info_request = comm.gen_request(token=token)
    info_request.add_request(
        'RemoveDistributionListMemberRequest',
        {
            'id': dlId,
            'dlm': {
                '_content': member
            }
         },
         'urn:zimbraAdmin'
    )
    info_response = comm.send_request(info_request)
    if not info_response.is_fault():
        zimbra_data = info_response.get_response()['RemoveDistributionListMemberResponse']
    else:
        print(info_response.get_fault_message())
        sys.exit(1)

# main program
options = getOptions()
config = readJson(options.config)
dlnew = readJson(options.distribution)

token = getToken(url=config['url'], user=config['user'], password=config['password'])
current = getDlData(name=dlnew['name'], url=config['url'], token=token)
if options.verbose:
    print("Current settings of distribution list {}:".format(current['name']))
    print(json.dumps(current, indent=2))
    print("Data read from {}:".format(options.distribution))
    print(json.dumps(dlnew, indent=2))

new_members = (list(set(dlnew['members']) - set(current['members'])))
obs_members = (list(set(current['members']) - set(dlnew['members'])))

for member in new_members:
    addMembers(current['id'], member, config['url'], token)

for member in obs_members:
  delMembers(current['id'], member, config['url'], token)
