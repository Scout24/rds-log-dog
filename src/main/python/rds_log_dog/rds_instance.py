
class RDSInstance(object):

    def __init__(self, name):
        self.name = name

    def get_id(self):
        return self.name
