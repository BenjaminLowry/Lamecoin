import time
import hashlib


class Transaction:

    def __init__(self):

        self._id = "23a4390de3487f"

        self._hash = ""

        self._timestamp = time.time()

        # Todo: Create Transaction Input and Output classes for handling of transaction data
        self._transaction_inputs = []

        self._transaction_output = []

        # Base hash off of the id and transaction data
        self._hash = hashlib.sha256([self._id, self._transaction_inputs, self._transaction_output])

