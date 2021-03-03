from Blocks.Block import Block


class Blockchain:
    difficulty = 4

    # initialize Blockchain object
    def __init__(self):
        self.blockchain = []

    # add a block to the blockchain
    def add_block(self, block):
        self.blockchain.append(block)

    # remove a block from the blockchain (ONLY USED FOR DEBUG PURPOSES)
    def remove_block(self, block):
        self.blockchain.remove(block)

    # mine the given block
    def mine_block(self, block):
        try:
            block.block_previous_hash = self.blockchain[-1].hash()
        except IndexError:
            block.block_previous_hash = "0" * 128  # Hash length in hex for SHA-512 is 128 characters

        while True:
            block.block_hash = block.hash()
            if block.block_hash[:self.difficulty] == "0" * self.difficulty:
                self.add_block(block)
                break
            else:
                block.block_nonce += 1

    # Verify the validity of the blockchain
    # TODO: Fix the function so that it properly detects corruption of the blockchain
    # Currently, it only says corrupt when the first block is tampered with
    def is_blockchain_valid(self):
        # If there's only the genesis block in the blockchain, it's automatically valid
        if len(self.blockchain) == 1:
            return "True (only genesis block in blockchain)"
        for i in range(1, len(self.blockchain)):
            _block_previous_hash = self.blockchain[i].block_previous_hash
            _block_current_hash = Block.hash(self.blockchain[i - 1])

            # block must have gotten tampered if the hashes of the same block differ
            if _block_previous_hash != _block_current_hash or _block_current_hash[:self.difficulty] != "0" * self.difficulty:
                return False
            # returns True since the blocks passed the hash checks
            return True
