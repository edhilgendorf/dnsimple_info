from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
from requests import Request, Session
import requests
__metaclass__ = type

def build_url(account, key, is_sandbox):
    headers={'Accept': 'application/json',
             'Authorization': 'Bearer ' + key }
    pre_url = ""
    if is_sandbox == True:
        pre_url = 'https://api.sandbox.dnsimple.com/v2/'
    else:
        pre_url = 'https://api.dnsimple.com/v2/'
    url = pre_url + account
    req = Request(url=url, headers=headers)
    prepped_request = req.prepare()
    return prepped_request

def iterate_data(request_object):
    data = []
    response = Session().send(request_object)
    return response.json()
    if response.json()["pagination"]["total_pages"]:
        pages = response.json()["pagination"]["total_pages"]
        for p in range(pages):
            p = p + 1
            request_object.url = request_object.url + '&page=' + str(p)
            new_results = Session().send(request_object)
            if new_results.json()["data"][0]:
                data.append(new_results.json()["data"][0])
        return(data)
    else:
        return response.json()

def record_info(account, key, domain, record, req_obj):
    req_obj.url, req_obj.method = req_obj.url + '/zones/' + domain + '/records?name=' + record, 'GET'
    return iterate_data(req_obj)

def domain_info(account, key, domain, req_obj):
    req_obj.url, req_obj.method = req_obj.url + '/zones/' + domain + '/records?per_page=1', 'GET'
    resp = Session().send(req_obj)
    return iterate_data(req_obj)

def account_info(account, key, req_obj):
    req_obj.url, req_obj.method = req_obj.url + '/zones/?per_page=1', 'GET'
    return iterate_data(req_obj)

def main():
    # define available arguments/parameters a user can pass to the module
    fields = {
        "account_id": {"required": True, "type": "str"},
        "api_key": {"required": True, "type": "str"},
        "name": {"required": False, "type": "str"},
        "record": {"required": False, "type": "str"},
        "sandbox": {"required": True, "type": "bool"}
        }

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode=False
    )

    params = module.params
    req = build_url(params['account_id'],
                    params['api_key'],
                    params['sandbox'])

    #If we have a record return info on that record
    if params['name'] and params['account_id'] and params['api_key'] and params['record']:
        result['dnsimple_info'] = record_info(params['account_id'],
                                              params['api_key'],
                                              params['name'],
                                              params['record'],
                                              req)

    #If we have the account only and domain, return records for the domain
    elif params['name'] and params['account_id'] and params['api_key']:
        #result['dnsimple_info'] = { "test": "success" }
        result['dnsimple_info'] = domain_info(params['account_id'],
                                              params['api_key'],
                                              params['name'], req)
    #If we have the account only, return domains
    elif params['account_id'] and params['api_key']:
        result['dnsimple_info'] = account_info(params['account_id'],
                                               params['api_key'], req)

    module.exit_json(**result)

if __name__ == '__main__':
    main()
