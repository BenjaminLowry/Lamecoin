import Block

from urllib.parse import urlparse
import hashlib

class Blockchain:

    def __init__(self):

        # Initialize Genesis Block (first block)
        # Todo: Change these transactions from text to actual transactions
        genesis_block_transactions = ["Ben gave 3 coins to SQ", "SQ gave 2 coins to PizzaHut"]
        genesis_block = Block(0, genesis_block_transactions)

        # Create new blockchain with Genesis Block
        self._chain = [genesis_block]

        self._current_transactions = []

        self._nodes = set()

    # Get genesis block
    def get_genesis_block(self):
        return self._chain[0]

    # Get the newest block from the blockchain
    def get_latest_block(self):
        return self._chain[-1]

    # Add a new block to the blockchain
    def generate_new_block(self):

        # Get most recent block
        previous_block = self.get_latest_block()

        # Set index of new block to the previous block + 1
        index = previous_block.index + 1

        # Get the block hash of the previous block
        previous_hash = previous_block.get_block_hash()

        # Initialize the new block
        new_block = Block(index, previous_hash)

        # Add the block to the blockchain
        self._chain.append(new_block)

        # Return the new block
        return new_block

    # Add a new block to the blockchain, assuming it is valid
    def add_new_block(self, new_block):
        if self.is_valid_new_block(self.get_latest_block(), new_block):
            self._chain.append(new_block)

    # Check whether a new block is valid
    def is_valid_new_block(self, previous_block, new_block):

        valid = False

        # Check cases in which the block is not valid
        if previous_block.index + 1 != new_block.index:
            print("Invalid index.")
        elif previous_block.block_hash != new_block.previous_hash:
            print("Invalid previous hash.")
        elif new_block.hash_block() != new_block.get_hash():
            print("Invalid hashes: " + new_block.hash_block() + " " + new_block.get_hash())
        else:
            valid = True

        return valid

    # Checking if an incoming chain is valid
    def is_valid_new_chain(self, disputed_chain):

        if disputed_chain[0].get_hash() != self.get_genesis_block().get_hash():
            print("Invalid genesis block.")
            return False

        for i in range(1, len(self._chain)):

            # Check if the blocks connect together properly
            if self.is_valid_new_block(disputed_chain[i - 1], disputed_chain[i]):
                pass
            else:
                return False

        return True

    # Resolve disputes between two different chains
    def replace_chain(self, new_chain):

        if self.is_valid_new_chain(new_chain) and len(new_chain) > len(self._chain):
            print("Valid chain will replace old chain.")

            self._chain = new_chain

        else:
            print("Invalid chain. Will not replace.")

    # Handles the proof of work algorithm, in order to prove work has been done
    def proof_of_work(self, last_block):

        """

        Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp'h) contains leading "12389"
        - Where p is the previous proof, p' is the new proof, and h is the previous hash

        :param last_block: <dict> last Block
        :return: <int> new proof

        """

        last_proof = last_block.get_proof()
        last_hash = last_block.get_hash()

        new_proof = 0

        while self.is_valid_proof(last_proof, new_proof, last_hash) is False:
            new_proof += 1

        return new_proof

    # Checks if the proof sent in is valid, proving work
    def is_valid_proof(self, last_proof, new_proof, last_hash):

        """

        :param last_proof: <int> Proof from last block
        :param new_proof: <int> Proof being guessed
        :param last_hash: <str> Hash of the last block
        :return: <bool> Whether the proof is valid or not

        """


        guess = f'{last_proof}{new_proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:5] == "12389"

    # Adds a new node to the server
    def register_node(self, node_address):

        """

        :param node_address: Address of node. Eg. 'http://192.168.0.5:5000'

        """

        parsed_url = urlparse(node_address)
        if parsed_url.netloc:
            self.nodes.ad.addd(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

