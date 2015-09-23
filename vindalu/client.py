import json
import os

import requests

from types import *

class Creds(object):
    username = None
    password = None

class BaseClient(object):

    def __init__(self, host="localhost", port=5454):
        self._base_url = "http://%s:%d" % (host, port)

        self.creds = self._load_creds()
        self.config = self.get_config()

        self.api_url = "%s/%s" % (self._base_url, self.config["api_prefix"])

    def get_config(self):
        resp = requests.get("%s/config" % (self._base_url))
        return resp.json()

    def _request(self, method, endpoint, params=None, data=None):
        req_url = "%s/%s" % (self.api_url, endpoint)

        if method in ("POST", "PUT", "DELETE"):
            auth = (self.creds.username, self.creds.password)
        else:
            auth = None

        resp = requests.request(method, req_url, auth=auth, params=params, data=data)
        return resp.json()

    def _load_creds(self):
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

    def get(self, atype, _id, version=0):
        if version > 0:
            obj = self._request("GET", "/%s/%s" % (atype, _id), params={"version": version})
        else:
            obj = self._request("GET", "/%s/%s" % (atype, _id))

        return Asset(obj["id"], obj["type"], obj["timestamp"], data=obj["data"])


    def get_version(self, atype, _id, diff=False):
        if diff:
            return self._request("GET", "/%s/%s/versions?diff" % (atype, _id))
        else:
            objs = self._request("GET", "/%s/%s/versions" % (atype, _id))
            return [ Asset(obj["id"], obj["type"], obj["timestamp"], data=obj["data"])
                for obj in objs ]

    def list_type_properties(self, atype):
        return self._request("GET", "/%s/properties" % (atype))

    def get_type(self):
        jobj = self._request("GET", "/")
        return [ TypeCount(**j) for j in jobj ]

    def create(self, atype, _id, data):
        jdata = json.dumps(data)
        return self._request("POST", "/%s/%s" % (atype, _id), data=jdata)

    def update(self, atype, _id, data):
        jdata = json.dumps(data)
        return self._request("PUT", "/%s/%s" % (atype, _id), data=jdata)

    def delete(self, atype, id):
        return self._request("DELETE", "/%s/%s" % (atype, id))

