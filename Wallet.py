

class Wallet:

    def __init__(self, identifier):

        self._identifier = identifier

        self._transactions = []

        self._value = 0

    def credit(self, value, transaction):
        self._value += value
        self._transactions.append(transaction)

    def debit(self, value, transaction):
        self._value -= value
        self._transactions.append(transaction)

    def get_value(self):
        return self._value
