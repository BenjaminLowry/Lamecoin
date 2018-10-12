import hashlib
import time
import json


class Block:

    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):

        self._index = index

        if timestamp is None:
            self._timestamp = time.time()
        else:
            self._timestamp = timestamp

        self._previous_hash = previous_hash
        self._transactions = transactions

        # Proof for proof-of-work algorithm
        self._proof = proof

        # Hash the block
        self._hash = self.hash_block()

    # For converting dictionary data into Block object
    @staticmethod
    def from_dict(data):
        return Block(data['index'], data['previous-hash'],
                   data['transactions'], data['proof'], data['timestamp'])

    # Returns a hexadecimal hash for the block
    def hash_block(self):
        block_data = json.dumps(self.to_jsonable_object(), sort_keys=True).encode()
        return hashlib.sha256(block_data).hexdigest()

    # Add transactions to block
    def add_transactions(self, transactions):
        # Todo: Add verification step
        self._transactions.append(transactions)

    def to_jsonable_object(self):
        return {
            'index': self._index,
            'timestamp': self._timestamp,
            'previous-hash': self._previous_hash,
            'transactions': self._transactions,
            'proof': self._proof
        }

    # Getter functions
    def get_index(self):
        return self._index

    def get_previous_hash(self):
        return self._previous_hash

    def get_transactions(self):
        return self._transactions

    def get_proof(self):
        return self._proof

    def get_hash(self):
        return self._hash

    def get_timestamp(self):
        return self._timestamp


