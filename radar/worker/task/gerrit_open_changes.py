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


class ProcessOpenChanges():

    def __init__(self):
        self._requests = list()
        self._responses = list()
        self._uri = "https://review.openstack.org"
        self._pp = pprint.PrettyPrinter(indent=4)
        self._systems_resource = '/systems'
        self._operators_resource = '/operators'
        self._changes_resource = '/changes'
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
        url = "%s/a/changes/?q=status:open" % (self._uri)
        self._requests.append(urllib2.Request(url));
        self._responses.append(urllib2.urlopen(self._requests[0]))

    def process_changes(self):
        processed=0
        for index, line in enumerate(self._responses[0]):
            if index > 0:
                if line.find('project') > -1:
                    project = line[line.rfind(":")+3:line.rfind('"')]
                if line.find('topic') > -1:
                    topic = line[line.rfind(":")+3:line.rfind('"')]
                if line.find('subject') > -1:
                    subject = line[line.rfind(":")+3:line.rfind('"')]
                if line.find('change_id') > -1:
                    change_id = line[line.rfind(":")+3:line.rfind('"')]
                    change = {"change_id": change_id}
                if line.find('status') > -1:
                    status = line[line.rfind(":")+3:line.rfind('"')]
                    print "\nprocessing change: %s" % change_id
                    print "  project: %s" % project
                    print "  subject: %s" % subject
                    print "  topic: %s" % topic
                    print "  status: %s" % status
                    if not self.change_exists(self._changes_resource, change):
                        change = { "change_id": change_id,
                                   "project": project,
                                   "topic": topic,
                                   "subject": subject,
                                   "status": status,
                                   "updated_at": datetime.utcnow().isoformat()}
                        print "  change does not exist, adding to database ..."
                        if self._responses.append(self.post_json(self._changes_resource, change)):
                            thechange = json.loads(self._responses[1].text)
                            success=True
                            change_id=''
                            try:
                                change_id = thechange['change_id']
                                url = "%s/%d" % (self._changes_resource, change_id)
                                thechange = self.get_json(url)
                            except KeyError as ke:
                                print "KeyError: %s change %s update failed" % (ke.toString(), change_id)
                                success=False
                            finally:
                                self._responses.remove(self._responses[1])
                            if success:
                                print "change successfully imported"
                                
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
        
    def change_exists(self, path, change, headers=None, status=None):
        try:
            response = self.get_json(path + "/" + change['change_id'])
            if response.status_code == requests.codes.ok:
                print "%s has already been imported" % change['change_id']
                return True
            else:
                return False
        except KeyError as ke:
            print "key error: %s" % ke.tostring()
            return False

    def do_update(self):
        self.__init__()
        self.get_credentials()
        self.process_changes()

if __name__ == "__main__":
    process = ProcessOpenChanges()
    process.do_update()
