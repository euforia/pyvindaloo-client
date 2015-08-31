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

        self.creds = self.__loadCreds()
        self.config = self.__getConfig()
        
        self.api_url = "%s/%s" % (self.__base_url, self.config["api_prefix"])

    def __getConfig(self):
        resp = requests.get("%s/config" % (self.__base_url))
        return resp.json()

    def _doRequest(self, method, endpoint, params=None, data=None):
        req_url = "%s/%s" % (self.api_url, endpoint)
        
        if method in ("post", "put", "delete"):
            auth = (self.creds.username, self.creds.password)
        else:
            auth = None

        if data != None:
            resp = eval("requests.%s(req_url, auth=auth, params=params, data=data)" % (
                method.lower()))
        else:
            resp = eval("requests.%s(req_url, params=params, auth=auth)" % (
                method.lower()))

        #{ "error": }
        return resp.json()

    def __loadCreds(self):
        fh = open(os.environ['HOME'] + "/.vindaloo/credentials", "r")
        jcreds = json.load(fh)
        fh.close()

        creds = Creds()
        creds.username = jcreds["auth"]["username"]
        creds.password = jcreds["auth"]["password"]
        return creds


class Client(BaseClient):

    def Get(self, atype, _id, version=0):
        if version > 0:
            obj = self._doRequest("get", "/%s/%s" % (atype, _id), params={"version": version})
        else:
            obj = self._doRequest("get", "/%s/%s" % (atype, _id))

        return Asset(obj["id"], obj["type"], obj["timestamp"], data=obj["data"])


    def GetVersions(self, atype, _id, diff=False):
        if diff:
            return self._doRequest("get", "/%s/%s/versions?diff" % (atype, _id))
        else:
            objs = self._doRequest("get", "/%s/%s/versions" % (atype, _id))
            return [ Asset(obj["id"], obj["type"], obj["timestamp"], data=obj["data"]) 
                for obj in objs ]

    def ListTypeProperties(self, atype):
        return self._doRequest("get", "/%s/properties" % (atype))        

    def GetTypes(self):
        jobj = self._doRequest("get", "/")
        return [ TypeCount(**j) for j in jobj ]


    def Create(self, atype, _id, data):
        jdata = json.dumps(data)
        return self._doRequest("post", "/%s/%s" % (atype, _id), data=jdata)

    def Update(self, atype, _id, data):
        jdata = json.dumps(data)
        return self._doRequest("put", "/%s/%s" % (atype, _id), data=jdata)

    def Delete(self, atype, id):
        return self._doRequest("delete", "/%s/%s" % (atype, id))

