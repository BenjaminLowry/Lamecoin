

class Wallet:

    def __init__(self, password):

        self._password = password
        self._private_key = "2ad79039ef93849dbc939"

        self._transactions = []

        self._value = 0
