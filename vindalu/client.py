import json
import os

import requests

from types import *

class Creds(object):
    username = None
    password = None

class BaseClient(object):

    def __init__(self, host="localhost", port=5454):
        self.__base_url = "http://%s:%d" % (host, port)

        self.creds = self._loadCreds()
        self.config = self.GetConfig()

        self.api_url = "%s/%s" % (self.__base_url, self.config["api_prefix"])

    def GetConfig(self):
        resp = requests.get("%s/config" % (self.__base_url))
        return resp.json()

    def _doRequest(self, method, endpoint, params=None, data=None):
        req_url = "%s/%s" % (self.api_url, endpoint)

        if method in ("POST", "PUT", "DELETE"):
            auth = (self.creds.username, self.creds.password)
        else:
            auth = None

        resp = requests.request(method, req_url, auth=auth, params=params, data=data)
        return resp.json()

    def _loadCreds(self):
        credsfile = os.environ['HOME'] + "/.vindalu/credentials"
        if !os.exists(credsfile):
            print "Creds file not found: %s" % (credsfile)
            exit(2)

        fh = open(credsfile, "r")
        jcreds = json.load(fh)
        fh.close()

        creds = Creds()
        creds.username = jcreds["auth"]["username"]
        creds.password = jcreds["auth"]["password"]
        return creds


class Client(BaseClient):

    def Get(self, atype, _id, version=0):
        if version > 0:
            obj = self._doRequest("GET", "/%s/%s" % (atype, _id), params={"version": version})
        else:
            obj = self._doRequest("GET", "/%s/%s" % (atype, _id))

        return Asset(obj["id"], obj["type"], obj["timestamp"], data=obj["data"])


    def GetVersions(self, atype, _id, diff=False):
        if diff:
            return self._doRequest("GET", "/%s/%s/versions?diff" % (atype, _id))
        else:
            objs = self._doRequest("GET", "/%s/%s/versions" % (atype, _id))
            return [ Asset(obj["id"], obj["type"], obj["timestamp"], data=obj["data"])
                for obj in objs ]

    def ListTypeProperties(self, atype):
        return self._doRequest("GET", "/%s/properties" % (atype))

    def GetTypes(self):
        jobj = self._doRequest("GET", "/")
        return [ TypeCount(**j) for j in jobj ]


    def Create(self, atype, _id, data):
        jdata = json.dumps(data)
        return self._doRequest("POST", "/%s/%s" % (atype, _id), data=jdata)

    def Update(self, atype, _id, data):
        jdata = json.dumps(data)
        return self._doRequest("PUT", "/%s/%s" % (atype, _id), data=jdata)

    def Delete(self, atype, id):
        return self._doRequest("DELETE", "/%s/%s" % (atype, id))

