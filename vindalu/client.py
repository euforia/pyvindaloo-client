import json
import os

import requests
import urlparse
import sys
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

log = logging.getLogger(__name__)

from types import *

class Creds(object):
    username = None
    password = None


class AssetExists(Exception):
    pass

class Unauthorized(Exception):
    pass

class Failed(Exception):
    pass

class BaseClient(object):

    def __init__(self, host="localhost", port=5454, username=None, password=None):
        self._base_url = "http://%s:%d" % (host, port)

        self.creds = self._load_creds()
        if username: self.creds.username = username
        if password: self.creds.password = password
        self.config = self.get_config()

        self.api_url = self._clean_uri("%s/%s" % (self._base_url, self.config["api_prefix"]))

    def get_config(self):
        resp = requests.get("%s/config" % (self._base_url))
        return resp.json()

    def _request(self, method, endpoint, params=None, data=None):

        req_url = "%s/%s" % (self.api_url, endpoint)
        log.debug("Request: %s", req_url)

        if method in ("POST", "PUT", "DELETE"):
            auth = (self.creds.username, self.creds.password)
        else:
            auth = None

        resp = requests.request(method, req_url, auth=auth, params=params, data=data)
        log.debug("Got response: %s", resp)

        if resp.status_code == 404:
            log.error(resp.text)
            return None
        elif resp.status_code == 401:
            raise Unauthorized()
        elif resp.status_code == 400 and resp.text.startswith('Asset already exists'):
            raise AssetExists()
        elif resp.status_code != 200:
            log.error("Got response: %s %s", resp, resp.text)
            raise Failed()

        return resp.json()

    def _load_creds(self):
        credsfile = os.environ['HOME'] + "/.vindalu/credentials"
        if not os.path.exists(credsfile):
            print "Creds file not found: %s" % (credsfile)
            exit(2)

        fh = open(credsfile, "r")
        jcreds = json.load(fh)
        fh.close()

        creds = Creds()
        creds.username = jcreds["auth"]["username"]
        creds.password = jcreds["auth"]["password"]
        return creds

    def _clean_uri(self, uri):
        return urlparse.urlunparse(urlparse.urlparse(uri))


class Client(BaseClient):

    def list_type_properties(self, atype):
        return self._request("GET", "/%s/properties" % (atype))

    def get_types(self):
        jobj = self._request("GET", "/")
        log.debug("Got response object: %s", jobj)
        return [ TypeCount(**j) for j in jobj ]

    def get(self, atype, _id, version=0):
        if version > 0:
            obj = self._request("GET", "/%s/%s" % (atype, _id), params={"version": version})
        else:
            obj = self._request("GET", "/%s/%s" % (atype, _id))

        if not obj:
            return obj
        return Asset(obj["id"], obj["type"], obj["timestamp"], data=obj["data"])

    def get_version(self, atype, _id, diff=False):
        if diff:
            return self._request("GET", "/%s/%s/versions?diff" % (atype, _id))
        else:
            objs = self._request("GET", "/%s/%s/versions" % (atype, _id))
            return [ Asset(obj["id"], obj["type"], obj["timestamp"], data=obj["data"])
                for obj in objs ]

    def create(self, atype, _id, data):
        jdata = json.dumps(data)
        return self._request("POST", "/%s/%s" % (atype, _id), data=jdata)

    def update(self, atype, _id, data):
        jdata = json.dumps(data)
        return self._request("PUT", "/%s/%s" % (atype, _id), data=jdata)

    def delete(self, atype, _id):
        return self._request("DELETE", "/%s/%s" % (atype, _id))


    def get_type(self, atype, version=0):
        if version > 0:
            obj = self._request("GET", "/%s" % (atype), params={"version": version})
        else:
            objs = self._request("GET", "/%s" % (atype))

        if not objs:
            return objs
        return [ Asset(obj["id"], obj["type"], obj["timestamp"], data=obj["data"])
                for obj in objs ]

    def create_type(self, atype, data):
        jdata = json.dumps(data)
        return self._request("POST", "/%s" % (atype), data=jdata)

    def update_type(self, atype, data):
        jdata = json.dumps(data)
        return self._request("PUT", "/%s" % (atype), data=jdata)

    def delete_type(self, atype):
        return self._request("DELETE", "/%s" % (atype))

