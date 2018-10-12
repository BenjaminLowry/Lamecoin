from Blockchain import Blockchain
from Block import Block
from Node import Node

from uuid import uuid4

from flask import Flask, jsonify, request

import requests
import time

from threading import Thread

# Create blockchain
blockchain = Blockchain()

# When a client node successfully provides the proof, timestamp will be stored here
mt = None

# Instantiate Node
# __name__ in this case equals "__main__"
app = Flask(__name__)

# Create unique identifier for node
node_identifier = str(uuid4()).replace("-", "")

# ******
# Change these params as they will be used for starting your server
# ******
app_host = "0.0.0.0"
app_port = "5001"


# Used to initialize a new master node onto the network, or the origin node
@app.route('/init', methods=['POST'])
def initialize_node():

    values = request.get_json()

    peer_host = values.get('peer-host')
    peer_port = values.get('peer-port')

    new_node_data = {
        'address': f"{app_host}:{app_port}"
    }

    # If no master nodes have been created yet, create the origin node
    if peer_host == app_host and peer_port == app_port:

        address = f"{app_host}:{app_port}"
        blockchain.register_master_node(address)

        response = {
            'message': 'Origin node registered.'
        }

        return jsonify(response), 201

    data = requests.post(f"http://{peer_host}:{peer_port}/node/master-register", json=new_node_data).json()

    response = {
        'message': 'New master node initialized.',
        'master-node-list': data['updated-node-list']
    }

    return jsonify(response), 201


# Registers a new master node with the blockchain and updates all other masters on the network
@app.route('/node/master-register', methods=['POST'])
def register_master():

    values = request.get_json()

    new_master_address = values.get('address')

    new_node_list = blockchain.register_master_node(new_master_address)

    t = Thread(target=update_master_nodes, args=[list(new_node_list)])
    t.start()

    response = {
        'message': 'New node registered.',
        'updated-node-list': list(new_node_list)
    }

    return jsonify(response), 201


# Posts the new list of master nodes to all master nodes on the network
def update_master_nodes(node_list):

    new_node_data = {
        'updated-node-list': list(node_list)
    }

    for node_address in node_list:

        requests.post(f"http://{node_address}/node/master-list-update", json=new_node_data)


# Called when receiving an updated list of master nodes
@app.route('/node/master-list-update', methods=['POST'])
def receive_updated_node_list():

    master_nodes = request.get_json().get('updated-node-list')

    blockchain.update_master_nodes(master_nodes)

    response = {
        'message': f"Nodes updated successfully by http://{app_host}:{app_port}"
    }
    print(response)

    return jsonify(response), 201


# Procedure for registering a new client node onto this master's sub-network
@app.route('/node/client-register', methods=['POST'])
def register_client():

    # Get the data from the client node requesting to be added to the network
    values = request.get_json()

    # Get the address of the new node
    node_address = values.get('address')
    node_identifier = values.get('identifier')

    if node_address is None:
        return "Error: please supply a valid node", 400

    new_node = Node(node_address, node_identifier)

    # Add the node to the blockchain
    blockchain.register_client_node(new_node)

    # Create response to client node
    response = {
        'message': 'New node added successfully to the network.'
    }

    return jsonify(response), 201


# Called to deliver latest block to a client node trying to mine it
@app.route('/get-latest-block', methods=['GET'])
def return_latest_block():

    # Get the JSON representing the latest block
    block_json = blockchain.get_latest_block().to_jsonable_object()

    print("block retrieved")
    return jsonify(block_json), 200


# Called when client nodes want to try and mine a block and are supplying the correct proof
@app.route('/give-proof', methods=['POST'])
def receive_proof_from_client():

    print("proof give start")

    global mt

    values = request.get_json()

    block_index = values.get("block-index")
    proof = values.get("proof")
    node_address = values.get("node-identifier")

    # If this block hasn't been mined yet
    if blockchain.get_length() - 1 == block_index and mt is None:

        print("valid start")

        latest_block = blockchain.get_latest_block()
        if Blockchain.is_valid_proof(latest_block.get_proof(), proof, latest_block.get_hash()):

            mt = time.time()

            for master_node_address in blockchain.get_master_nodes():

                if master_node_address == f"{app_host}:{app_port}":
                    continue

                time_data = {
                    'mine-timestamp': mt
                }

                data = requests.post(f"http://{master_node_address}/verify-mine", json=time_data).json()

                print("verify complete for " + master_node_address)

                if data['valid']:
                    continue
                elif not data['valid']:  # If another client beat this client to the block

                    mt = None
                    response = {
                        'success': False
                    }
                    return jsonify(response), 201

            # Receive a reward for mining the coin (reward = 1 coin)
            blockchain.new_transaction(
                sender="0",
                recipient=node_address,
                amount=1
            )

            new_block, queued_transactions = blockchain.generate_new_block(proof)

            mt = None

            response = {
                'success': True,
                'new-block': new_block.to_jsonable_object(),
                'queued-transactions': queued_transactions
            }

            t = Thread(target=update_master_blockchains, args=(new_block,))
            t.start()

            th = Thread(target=complete_transactions, args=(queued_transactions,))
            th.start()

            return jsonify(response), 201

    response = {
        'success': False
    }

    return jsonify(response), 201


# When a block is mined, the master node will POST its timestamp to all of the other master nodes and check if another
# master node has a client node that beat the time, as a form of verification
@app.route('/verify-mine', methods=['POST'])
def verify_mine():

    global mt

    values = request.get_json()

    timestamp = values.get('mine-timestamp');

    if mt is not None:

        if timestamp < mt:

            response = {
                'valid': True
            }
            return jsonify(response), 201

        elif mt > timestamp:

            response = {
                'valid': False
            }
            return jsonify(response), 201

    response = {
        'valid': True
    }
    return jsonify(response), 201


# Called when a client node is passing a new transaction to this master node
@app.route('/transaction/receive', methods=['POST'])
def receive_transaction():

    values = request.get_json()

    blockchain.new_transaction(
        sender=values['sender'],
        recipient=values['recipient'],
        amount=values['amount']
    )

    response = {
        'success': True
    }
    return jsonify(response), 201


# Completes the queued transactions once their block has been mined
def complete_transactions(transactions):

    for transaction in transactions:

        sender_address = ""
        recipient_address = ""

        for master_node in blockchain.get_master_nodes():

            client_nodes = requests.get(f'http://{master_node}/get-client-nodes').json()['clients']

            for client_node in client_nodes:

                # If this client node is the sender in the transaction
                if transaction['sender'] == client_node['identifier']:
                    sender_address = client_node['address']

                # If this client node is the recipient in the transaction
                if transaction['recipient'] == client_node['identifier']:
                    recipient_address = client_node['address']

        if transaction['sender'] != '0':
            data_debit = requests.post(f"http://{sender_address}/transaction/debit", json=transaction)

        data_credit = requests.post(f"http://{recipient_address}/transaction/credit", json=transaction)


# Returns the full chain as JSON
@app.route('/get-chain', methods=['GET'])
def return_chain():

    response = {
        'blockchain': blockchain.get_jsonable_chain()
    }

    return jsonify(response), 200


# Returns a list of client nodes on this master's sub-network, so that other master nodes can complete transactions
@app.route('/get-client-nodes', methods=['GET'])
def return_client_nodes():

    clients = []

    for client_node in blockchain.get_client_nodes():

        clients.append({
            'address': client_node.get_address(),
            'identifier': client_node.get_identifier()
        })

    response = {
        'clients': clients
    }

    return jsonify(response), 200


# When one master updates the blockchain, it pushes the new blockchain to all other masters
def update_master_blockchains(new_block):

    print('updating other master nodes in the network...')
    for master_node_address in blockchain.get_master_nodes():

        if master_node_address != f"{app_host}:{app_port}":

            block_json = {
                'index': new_block.get_index(),
                'previous-hash': new_block.get_previous_hash(),
                'transactions': new_block.get_transactions(),
                'proof': new_block.get_proof(),
                'timestamp': new_block.get_timestamp()
            }

            requests.post(f"http://{master_node_address}/node/update-blockchain", json=block_json)
    print('finished sending new block to all other master nodes.')


# Called when a new updated blockchain is being sent to this master, overriding the current blockchain
@app.route('/node/update-blockchain', methods=['POST'])
def update_blockchain():

    print('receiving new block from other master node...')
    values = request.get_json()

    index = values['index']
    previous_hash = values['previous-hash']
    transactions = values['transactions']
    proof = values['proof']
    timestamp = values['timestamp']

    new_block = Block(index, previous_hash, transactions, proof, timestamp)

    blockchain.add_new_block(new_block)
    print('new block added.')

    response = {
        'success': True
    }

    return jsonify(response), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=app_port, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host=app_host, port=port)

