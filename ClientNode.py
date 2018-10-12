from Blockchain import Blockchain
from Block import Block
from Wallet import Wallet

from uuid import uuid4

from flask import Flask, jsonify, request

import requests

# Create unique identifier for node
node_identifier = str(uuid4()).replace("-", "")
wallet_identifier = str(uuid4()).replace("-", "")

# Create blockchain
blockchain = Blockchain()

# Create wallet
wallet = Wallet(wallet_identifier)

nodes = set()

# Instantiate Node
# __name__ in this case equals "__main__"
app = Flask(__name__)

app_host = "0.0.0.0"
app_port = "5901"

master_address = ""


# Called to initialize the client node before it can perform tasks
@app.route('/init', methods=['POST'])
def initialize_node():

    # Get the master address data from the POST's JSON
    values = request.get_json()

    master_host = values.get("host")
    master_port = values.get("port")

    global master_address

    # Create the address for the master node (which the data will be sent to)
    master_address = master_host + ":" + master_port

    # Create the address for the new node
    node_address = app_host + ":" + app_port

    # Create the dictionary containing the new node's data to be sent to the master node
    new_node_data = {
        'address': node_address,
        'identifier': node_identifier
    }

    # POST the new node's data to the master node, and get the response
    requests.post(f'http://{master_address}/node/client-register', json=new_node_data)

    response = {
        'message': 'Node successfully initialized and added to the network.',
        'master-node': master_address,
        'node-identifier': node_identifier
    }

    return jsonify(response), 201


# Queries the master node for the current block and tries to mine it
@app.route('/mine', methods=['GET'])
def mine():

    values = requests.get(f'http://{master_address}/get-latest-block').json()

    # Get the new proof as the "cost" of mining a new block
    latest_block = Block.from_dict(values)
    proof = Blockchain.proof_of_work(latest_block)

    mine_request = {
        'proof': proof,
        'block-index': latest_block.get_index(),
        'node-identifier': node_identifier
    }

    print("got proof")

    # Send the proof to the master node
    values = requests.post(f'http://{master_address}/give-proof', json=mine_request).json()

    success = values.get("success")

    if success:  # If the mine was successful

        new_block = Block.from_dict(values.get("new-block"))
        queued_transactions = values.get("queued-transactions")

        response = {
            'message': 'New block mined',
            'index': new_block.get_index(),
            'transactions': new_block.get_transactions(),
            'proof': proof,
            'previous-hash': new_block.get_previous_hash()
        }
    else:  # If someone beat you to the block
        response = {
            'message': 'Mine failed. Other node found block first.'
        }

    return jsonify(response), 200


# Creates a new transaction queued on the master node's blockchain
@app.route('/transaction/new', methods=['POST'])
def new_transaction():

    # Get the information from the POST
    values = request.get_json()

    # Specify what the information must contain
    required_transaction_info = ['sender', 'recipient', 'amount']

    # Check that the new transaction contains all required fields
    if not all(k in values for k in required_transaction_info):
        return 'Missing values', 400

    requests.post(f'http://{master_address}/transaction/receive', json=values)

    response = {
        'message': 'New transaction queued'
    }

    return jsonify(response), 201


# Credits this client node from a completed transaction (i.e. this client node was the recipient of the transaction)
@app.route('/transaction/credit', methods=['POST'])
def credit_wallet():

    values = request.get_json()

    credit_value = values['amount']

    wallet.credit(credit_value, values)

    response = {
        'message': 'Credit successfully applied'
    }

    return jsonify(response), 201


# Debits this client node from a completed transaction (i.e. this client node was the sender of the transaction)
@app.route('/transaction/debit', methods=['POST'])
def debit_wallet():
    values = request.get_json()

    debit_value = values['amount']

    wallet.debit(debit_value, values)

    response = {
        'message': 'Debit successfully applied'
    }

    return jsonify(response), 201


# Called to get the current value of the client's wallet
@app.route('/wallet/get-value', methods=['GET'])
def get_wallet_value():

    response = {
        'value': wallet.get_value()
    }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=app_port, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host=app_host, port=port)

