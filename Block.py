import hashlib
import time


class Block:

    def __init__(self, index, previous_hash):

        self._index = index

        self._timestamp = time.time()

        self._previous_hash = previous_hash
        self._transactions = []

        # Hash the block
        self._hash = self.hash_block()

    # Returns a hexadecimal hash for the block
    def hash_block(self):
        return hashlib.sha256([hashlib.sha256(self._transactions), self._previous_hash]).hexdigest()

    # Add transactions to block
    def add_transactions(self, transactions):
        # Todo: Add verification step
        self._transactions.append(transactions)

    # Getter functions
    def get_previous_hash(self):
        return self._previous_hash

    def get_transactions(self):
        return self._transactions

    def get_hash(self):
        return self._hash


