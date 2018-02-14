from Blockchain import Blockchain

from uuid import uuid4

from flask import Flask, jsonify, request


# Create blockchain
blockchain = Blockchain()

# Instantiate Node
# __name__ in this case equals "__main__"
app = Flask(__name__)

# Create unique identifier for node
node_identifier = str(uuid4()).replace("-", "")


@app.route('/mine', methods=['GET'])
def mine():

    # Get the new proof as the "cost" of mining a new block
    last_block = blockchain.get_latest_block()
    proof = blockchain.proof_of_work(last_block)

    # Receive a reward for mining the coin (reward = 1 coin)
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1
    )

    previous_hash = last_block.get_previous_hash()
    new_block = blockchain.generate_new_block(proof)

    response = {
        'message': 'New block formed',
        'index': new_block.get_index(),
        'transactions': new_block.get_transactions(),
        'proof': proof,
        'previous-hash': previous_hash
    }

    return jsonify(response), 200


@app.route('/transaction/new', methods=['POST'])
def new_transaction():

    # Get the information from the POST
    values = request.get_json()

    # Specify what the information must contain
    required_transaction_info = ['sender', 'recipient', 'amount']

    # Check that the new transaction contains all required fields
    if not all(k in values for k in required_transaction_info):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {
        'message': 'New transaction queued',
        'index': index
    }

    return jsonify(response), 201


@app.route('/get-chain', methods=['GET'])
def return_chain():

    response = {
        'chain': blockchain.get_jsonable_chain(),
        'length': blockchain.get_length()
    }

    return jsonify(response), 200


@app.route('/node/register', methods=['POST'])
def register_node():

    values = request.get_json()

    nodes = values.get('nodes')

    if nodes is None:
        return "Error: please supply a valid list of nodes", 400
    else:
        for node in nodes:
            blockchain.register_node(node)

    response = {
        'message': 'New nodes were added.',
        'new-nodes': nodes,
        'total-nodes': list(blockchain.get_nodes())
    }

    return jsonify(response), 201


@app.route('/node/resolve', methods=['GET'])
def resolve():

    was_replaced = blockchain.resolve_conflicts()

    if was_replaced:
        response = {
            'message': 'Chain was replaced by peer copy.',
            'new-chain': blockchain.get_jsonable_chain()
        }
    else:
        response = {
            'message': 'Chain was correct and thus was left as-is',
            'chain': blockchain.get_jsonable_chain()
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)

