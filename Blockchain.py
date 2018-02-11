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

    # Get genesis block
    def get_genesis_block(self):
        return self._blockchain[0]

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

    # Add a new block to the blockchain, assuming it is valid
    def add_new_block(self, new_block):
        if self.is_valid_new_block(self.get_latest_block(), new_block):
            self._blockchain.append(new_block)

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

        for i in range(1, len(self._blockchain)):

            # Check if the blocks connect together properly
            if self.is_valid_new_block(disputed_chain[i - 1], disputed_chain[i]):
                pass
            else:
                return False

        return True

    # Resolve disputes between two different chains
    def replace_chain(self, new_chain):

        if self.is_valid_new_chain(new_chain) and len(new_chain) > len(self._blockchain):
            print("Valid chain will replace old chain.")

            self._blockchain = new_chain

        else:
            print("Invalid chain. Will not replace.")



