import Block


class BlockchainMain:

    def __init__(self):

        # Initialize Genesis Block (first block)
        # Todo: Change these transactions from text to actual transactions
        genesis_block_transactions = ["Ben gave 3 coins to SQ", "SQ gave 2 coins to PizzaHut"]
        genesis_block = Block(0, genesis_block_transactions)

        # Create new blockchain with Genesis Block
        self._blockchain = [genesis_block]

        # Create 2nd block and add it to block chain
        block2 = self.generate_new_block()

        block2.add_transactions(["Mr. Ronan gives 30 coins to Mr. Lee", "Mr. Lee gives 2 coins to his dog"])

    # Get the newest block from the blockchain
    def get_latest_block(self):
        return self._blockchain[-1]

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
        self._blockchain.append(new_block)

        # Return the new block
        return new_block
