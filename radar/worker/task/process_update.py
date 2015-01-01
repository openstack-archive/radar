import sys
import os
import urllib2
import httplib
import json
import pprint
import re
import requests
from urllib import urlencode
from datetime import datetime

from ConfigParser import ConfigParser


class ProcessCISystems():

    def __init__(self):
        self._requests = list()
        self._responses = list()
        self._uri = "https://review.openstack.org"
        self._pp = pprint.PrettyPrinter(indent=4)
        self._systems_resource = '/systems'
        self._operators_resource = '/operators'
        self.default_headers = {}

    def get_credentials(self):
        dashboardconfig = ConfigParser()
        dashboardconfig.readfp(open("/opt/.dashboardconfig"))
        username = dashboardconfig.get("review", "user")
        password = dashboardconfig.get("review", "password")

        passwordmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passwordmgr.add_password(None, self._uri, username, password)
        handler = urllib2.HTTPDigestAuthHandler(passwordmgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        # Make the request
        self._requests.append(urllib2.Request("%s/a/groups/95d633d37a5d6b06df758e57b1370705ec071a57/members/" % (self._uri)))
        self._responses.append(urllib2.urlopen(self._requests[0]))

    def process_systems(self):
        processed=0
        for index, line in enumerate(self._responses[0]):
            if index > 0:
                if line.find("account_id") > -1:
                    cis_account_id = line[line.rfind(":")+2:line.rfind(",")]
                if line.find("\"name\"") > -1:
                    cis_system_name = line[line.rfind(":")+3:line.rfind(",")-1]
                if line.find("\"email\"") > -1:
                    cis_operator_email = line[line.rfind(":")+3:line.rfind(",")-1]
                if line.find("\"username\"") > -1:
                    cis_operator_username = line[line.rfind(":")+3:line.rfind(",")-1]
                    print "username: %s" % cis_operator_username
                    system = {"name": cis_system_name}
                    print "Attempting to import %s" % cis_system_name
                    if not self.system_exists(self._systems_resource, system):
                        self._responses.append(self.post_json(self._systems_resource, system))
                        thesystem = json.loads(self._responses[1].text)
                        success=True
                        system_id=''
                        try:
                            system_id = thesystem['id']
                            url = "%s/%d" % (self._systems_resource, system_id)
                            thesystem = self.get_json(url)
                        except KeyError as ke:
                            print "System %s has already been imported" % cis_system_name
                            success=False
                        finally:
                            self._responses.remove(self._responses[1])
                        if success:
                            operator = {"system_id": system_id,
                                        "operator_name": cis_operator_username,
                                        "operator_email": cis_operator_email}
                            print 'updating operator: %s' % operator
                            self._responses.append(self.post_json(self._operators_resource, operator))
                            theoperator = json.loads(self._responses[1].text)
                            try:
                                operator_id = theoperator['id']
                                url = "%s/%d" % (self._operators_resource, operator_id)
                                theoperator = self.get_json(url)
                            except KeyError as ke:
                                pass
                            finally:
                                self._responses.remove(self._responses[1])
                    else:
                        system_id=''
                        success=True
                        try:
                            response = self.get_json(self._systems_resource + "/" + cis_system_name)
                            thesystem = json.loads(response.text)
                            system_id = thesystem['id']
                        except KeyError as ke:
                            print "Unable to retrieve system %s" % cis_system_name
                            success=False
                        if success:
                            print "put request for system_id: %s and system %s" % (system_id, cis_system_name)
                            system = { "system_id": system_id,
                                        "name": cis_system_name,
                                        "updated_at": datetime.utcnow().isoformat()}
                            self._responses.append(self.put_json(self._systems_resource, system))
                            thesystem = json.loads(self._responses[1].text)
                            success=True
                            system_id=''
                            try:
                                system_id = thesystem['id']
                                url = "%s/%d" % (self._systems_resource, system_id)
                                thesystem = self.get_json(url)
                            except KeyError as ke:
                                print "System %s update failed" % cis_system_name
                                success=False
                            finally:
                                self._responses.remove(self._responses[1])
                            if success:
                                print "system %s updated successfully" % system_id 
                                success=True
                                operator_id=''
                                try:
                                    response = self.get_json(self._operators_resource + "/" + cis_operator_username)
                                    theoperator = json.loads(response.text)
                                    operator_id = theoperator['id']
                                except KeyError as ke:
                                    print "Unable to retrieve operator %s" % cis_operator_username
                                    success=False
                                if success:
                                    success=True
                                    operator = {"operator_id": operator_id,
                                                "operator_name": cis_operator_username,
                                                "operator_email": cis_operator_email,
                                                "updated_at": datetime.utcnow().isoformat()}
                                    self._responses.append(self.put_json(self._operators_resource, operator))
                                    theoperator = json.loads(self._responses[1].text)
                                    try:
                                        operator_id = theoperator['id']
                                        operator_name = theoperator['operator_name']
                                        url = "%s/%d" % (self._operators_resource, operator_id)
                                        response = self.get_json(url)
                                    except KeyError as ke:
                                        success=False
                                    finally:
                                        self._responses.remove(self._responses[1])
                                
                                    if success:
                                        theoperator = json.loads(response.text)
                                        print "operator %s was updated successfully" % theoperator['operator_name']

    def _request_json(self, path, params, headers=None, method="post",
                      status=None, path_prefix="http://localhost/api/v1"):

        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)

        full_path = path_prefix + path
        if not headers:
            headers = {'content-type': 'application/json'}
        if method is "post":
            response = requests.post(str(full_path), data=json.dumps(params), headers=headers)
        elif method is "put":
            response = requests.put(str(full_path), data=json.dumps(params), headers=headers)
        else:   
            response = requests.get(str(full_path))

        return response


    def put_json(self, path, params, headers=None, status=None):
        return self._request_json(path=path, params=params, headers=headers,
                                  status=status, method="put")

    def post_json(self, path, params, headers=None, status=None):
        return self._request_json(path=path, params=params,
                                  headers=headers, 
                                  status=status, method="post")

    def get_json(self, path, headers=None, status=None):
        return self._request_json(path=path, params=None,
                                  headers=headers,
                                  status=status, method="get")
    def system_exists(self, path, system, headers=None, status=None):
        try:
            response = self.get_json(path + "/" + system['name'])
            if response.status_code == requests.codes.ok:
                print "%s has already been imported" % system['name']
                return True
            else:
                return False
        except KeyError as ke:
            return False

    def do_update(self):
        self.__init__()
        self.get_credentials()
        self.process_systems()

if __name__ == "__main__":
    process = ProcessCISystems()
    process.do_update()
