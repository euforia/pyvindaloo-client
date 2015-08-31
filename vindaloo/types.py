
class TypeCount(object):
    def __init__(self, name, count):
        self.name = name
        self.count = count

class Asset(object):

    def __init__(self, id, atype, timestamp, data):
        self.id = id
        self.type = atype
        self.timestamp = timestamp
        self.data = data