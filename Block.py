import hashlib
import time


class Block:

    def __init__(self, index, previous_hash):

        self._index = index

        self._timestamp = time.time()

        self._previous_hash = previous_hash
        self._transactions = []

        # Create a hash object based off of the transactions list and the previous block's hash
        hash_object = hashlib.sha256([hashlib.sha256(self._transactions), previous_hash])

        # Set block hash to hexadecimal hash of hash object
        self._block_hash = hash_object.hexdigest()

    # Add transactions to block
    def add_transactions(self, transactions):
        # Todo: Add verification step
        self._transactions.append(transactions)

    # Getter functions
    def get_previous_hash(self):
        return self._previous_hash

    def get_transactions(self):
        return self._transactions

    def get_block_hash(self):
        return self._block_hash


