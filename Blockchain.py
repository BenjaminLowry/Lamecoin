from Block import Block

from urllib.parse import urlparse
import hashlib
import requests
import json
import time


class Blockchain:

    def __init__(self):

        # Initialize Genesis Block (first block)
        genesis_block = Block(0, 1, [], 100, 100000)

        # Create new blockchain with Genesis Block
        self._chain = [genesis_block]

        self._current_transactions = []

        # Set of client nodes of type Node
        self._client_nodes = set()

        # Set of addresses of master node servers
        self._master_nodes = set()

    # Get the chain
    def get_chain(self):
        return self._chain

    # Get the chain in a JSON-friendly format
    def get_jsonable_chain(self):

        json_blocks = [block.to_jsonable_object() for block in self._chain]

        return json_blocks

    def get_length(self):
        return len(self._chain)

    # Get genesis block
    def get_genesis_block(self):
        return self._chain[0]

    # Get the newest block from the blockchain
    def get_latest_block(self):
        return self._chain[-1]

    # Add a new block to the blockchain
    def generate_new_block(self, proof):

        # Get most recent block
        previous_block = self.get_latest_block()

        # Set index of new block to the previous block + 1
        index = previous_block.get_index() + 1

        # Get the block hash of the previous block
        previous_hash = previous_block.get_hash()

        # Initialize the new block
        new_block = Block(index, previous_hash, self._current_transactions, proof)

        queued_transactions = self._current_transactions

        # Reset the current transactions list
        self._current_transactions = []

        # Add the block to the blockchain
        self._chain.append(new_block)

        # Return the new block
        return new_block, queued_transactions

    # Add a new block to the blockchain, assuming it is valid
    def add_new_block(self, new_block):
        if self.is_valid_new_block(self.get_latest_block(), new_block):
            self._chain.append(new_block)

    # Check whether a new block is valid
    @staticmethod
    def is_valid_new_block(previous_block, new_block):

        valid = False

        # Check cases in which the block is not valid
        if previous_block.get_index() + 1 != new_block.get_index():
            print("Invalid index.")
        elif previous_block.get_hash() != new_block.get_previous_hash():
            print("Invalid previous hash.")
        elif new_block.hash_block() != new_block.get_hash():
            print("Invalid hashes: " + new_block.hash_block() + " " + new_block.get_hash())
        else:
            valid = True

        return valid

    # Checking if an incoming chain is valid
    def is_valid_chain(self, disputed_chain):

        # Hash the incoming and current genesis block and check if they are the same
        if disputed_chain[0].get_hash() != self.get_genesis_block().get_hash():
            print("Invalid genesis block.")
            return False

        # Loop through the disputed chain
        for i in range(1, len(disputed_chain)):

            # Check if the blocks connect together properly
            if self.is_valid_new_block(disputed_chain[i - 1], disputed_chain[i]):
                pass
            else:
                return False

        return True

    # Handle a new incoming transaction
    def new_transaction(self, sender, recipient, amount):

        """

        :param sender: Address (Node identifier) of sender
        :param recipient: Address (Node identifier) of recipient
        :param amount: Amount of currency
        :return: Index of block that new transaction will belong to

        """

        # Add the transaction to the pending transactions list
        self._current_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "timestamp": time.time()
        })

        return self.get_latest_block().get_index() + 1

    '''
    # Find the most accurate chain if there is a dispute
    def resolve_conflicts(self):

        # Get all nodes from the network
        neighbors = self._nodes

        new_chain = None

        # Get length of current blockchain to make sure the new one is longer
        max_length = self.get_length()

        # Loop through neighbor nodes
        for node in neighbors:

            # GET the full chain from a node
            response = requests.get(f'http://{node}/get-chain')

            # If the GET is successful
            if response.status_code == 200:

                # Get chain as JSON and convert each block's data into Block objects
                chain = [Block.from_dict(block_data) for block_data in response.json()['chain']]
                # Get length from JSON
                length = response.json()['length']

                # If the chain is valid and is longer than the (currently) longest chain in the network
                if self.is_valid_chain(chain) and length > max_length:
                    new_chain = chain
                    max_length = length

        # If we successfully found a more accurate chain
        if new_chain:
            self._chain = new_chain
            return True
        else:
            return False
    '''
    # Handles the proof of work algorithm, in order to prove work has been done
    @staticmethod
    def proof_of_work(last_block):

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

        while Blockchain.is_valid_proof(last_proof, new_proof, last_hash) is False:
            new_proof += 1

        return new_proof

    # Checks if the proof sent in is valid, proving work
    @staticmethod
    def is_valid_proof(last_proof, new_proof, last_hash):

        """

        :param last_proof: <int> Proof from last block
        :param new_proof: <int> Proof being guessed
        :param last_hash: <str> Hash of the last block
        :return: <bool> Whether the proof is valid or not

        """

        guess = f'{last_proof}{new_proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:5] == "12389"

    # Return master nodes (in address form e.g. 'http://192.168.0.5:5000')
    def get_master_nodes(self):
        return self._master_nodes

    # Return client nodes
    def get_client_nodes(self):
        return self._client_nodes

    # Update the nodes (from other master's lists)
    def update_master_nodes(self, new_nodes):
        self._master_nodes = new_nodes

    # Adds a new client node of type Node
    def register_client_node(self, client_node):
        self._client_nodes.add(client_node)
        return self.get_client_nodes()

    # Adds a new master node of type String (address)
    def register_master_node(self, master_node):
        self._master_nodes.add(master_node)
        return self.get_master_nodes()

    # # Adds a new node to the server of type Node
    # def register_node(self, node_address, node_list):
    #
    #     """
    #
    #     :param node_address: Address of node. Eg. 'http://192.168.0.5:5000'
    #
    #     """
    #
    #     node_set = set(node_list)
    #
    #     parsed_url = urlparse(node_address)
    #     if parsed_url.netloc:
    #         node_set.add(parsed_url.netloc)
    #     elif parsed_url.path:
    #         # Accepts an URL without scheme like '192.168.0.5:5000'.
    #         node_set.add(parsed_url.path)
    #     else:
    #         raise ValueError('Invalid URL')
    #
    #     return node_set



