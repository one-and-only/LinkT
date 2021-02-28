from Blocks.Helpers import Helpers


# Class where block representations are stored
class Block:
    block_number = 0
    block_data = ""
    block_hash = ""
    block_previous_hash = ""
    block_nonce = 0

    # initialize Block object
    # SHA-512 hash length is 128 characters in hex
    def __init__(self, block_data, block_number=0, block_previous_hash="0" * 128, block_nonce=0):
        self.block_data = block_data  # block data
        self.block_previous_hash = block_previous_hash  # hash of the previous block
        self.block_number = block_number  # block number
        self.block_hash = self.hash()  # generate hash of the block
        self.block_nonce = block_nonce  # nonce of the block. Always start at 0

    # return the new hash of the block
    def hash(*args):
        return Helpers.update_hash(
            args[0].block_previous_hash, args[0].block_number, args[0].block_data, args[0].block_nonce
        )

    # return string representation of a block
    def __str__(self):
        return "Block Number: {}\nBlock Hash: {}\nPrevious Block Hash: {}\nBlock Data: {}\nBlock Nonce: {}\n".format(
            self.block_number, self.hash(), self.block_previous_hash, self.block_data, self.block_nonce
        )
