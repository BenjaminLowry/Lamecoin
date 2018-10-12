import time
import hashlib
from flask import jsonify
from enum import Enum


class Transaction:

    TRANSACTION_FEE = 1

    def __init__(self, type, data, id=None, timestamp=None):

        if id is None:
            # Todo: Create ID-generating function
            self._id = "23a4390de3487f"
        else:
            self._id = id

        self._hash = None

        if timestamp is None:
            self._timestamp = time.time()
        else:
            self._timestamp = timestamp

        self._type = type  # TransactionType.NORMAL

        self._data = {
            'inputs': data['inputs'],
            'outputs': data['outputs']
        }

        '''
        
        Input Structure:
        inputs: [{
            "transaction": "9e765ad30c...e908b32f0c", // transaction hash taken from a previous unspent transaction output (64 bytes)
            "index": "0", // index of the transaction taken from a previous unspent transaction output
            "amount": 5000000000, // amount of satoshis
            "address": "dda3ce5aa5...b409bf3fdc", // from address (64 bytes)
            "signature": "27d911cac0...6486adbf05" // transaction input hash: sha256 (transaction + index + amount + address) signed with owner address's secret key (128 bytes)
        }]
        
        Output Structure:
        outputs: [{
            "amount": 10000, // amount of satoshis
            "address": "4f8293356d...b53e8c5b25" // to address (64 bytes)
        }]
        
        '''

        # Base hash off of the id, timestamp, and transaction data
        self._hash = self.hash_transaction()

    def hash_transaction(self):
        return hashlib.sha256(self._id + self._timestamp + jsonify(self._data))

    def check_validity(self):

        if self._hash != self.hash_transaction():
            # Todo: Create Error Throwing Class
            print("Invalid transaction. Hashes do not match.")
            return

        input_sum = 0

        # Check that all the input transactions are valid
        for input in self._data['inputs']:

            # Count all of the input amounts
            input_sum += int(input['amount'])

            # Hash the contents of the transaction for verification step
            input_hash = hashlib.sha256(input['transaction'] + input['index'] + input['address'])

            # Verify that the signature on the transaction is correct
            is_valid = Transaction.verify_sign(input['address'], input['signature'], input_hash)

            if not is_valid:
                print("Invalid transaction. Signature is not correct.")
                return

        if self._type == TransactionType.NORMAL:

            output_sum = 0

            for output in self._data['outputs']:

                output_sum += int(output['amount'])

            # Check if more money is trying to be sent than left the inputs
            if output_sum > input_sum:
                print(f"Invalid transaction balance. Output sum: {output_sum} is greater than "
                      f"input sum: {input_sum}.")
                return
            # Check if there is sufficient amount to deduct fee
            elif input_sum - output_sum < self.TRANSACTION_FEE:
                print(f"Invalid transaction balance in order to deduct fee. Input sum: {input_sum}, "
                      f"output sum: {output_sum}.")
                return

        return True

    @staticmethod
    def verify_sign(public_key_loc, signature, data):

        """
        Verifies with a public key from whom the data came that it was indeed
        signed by their private key
        param: public_key_loc Path to public key
        param: signature String signature to be verified
        return: Boolean. True if the signature is valid; False otherwise.
        """

        from Crypto.PublicKey import RSA
        from Crypto.Signature import PKCS1_v1_5
        from Crypto.Hash import SHA256
        from base64 import b64decode

        pub_key = open(public_key_loc, "r").read()
        rsakey = RSA.importKey(pub_key)
        signer = PKCS1_v1_5.new(rsakey)
        digest = SHA256.new()
        # Assumes the data is base64 encoded to begin with
        digest.update(b64decode(data))
        if signer.verify(digest, b64decode(signature)):
            return True
        return False

    @staticmethod
    def from_json(json_data):
        transaction = Transaction(json_data['type'], json_data['data'], json_data['id'], json_data['timestamp'])
        return transaction


class TransactionType(Enum):
    NORMAL = 1
    REWARD = 2
    FEE = 3