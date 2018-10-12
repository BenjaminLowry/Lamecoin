

# Data storage method for client nodes on the network
class Node(object):

    def __init__(self, address, identifier):

        self._address = address

        self._identifier = identifier

    def get_address(self):
        return self._address

    def get_identifier(self):
        return self._identifier
