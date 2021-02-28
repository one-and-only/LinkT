# -*- coding: utf-8 -*-
# import all the required classes
from Blocks.Block import Block
from Blocks.Blockchain import Blockchain


def main():
    blockchain = Blockchain()  # create new blockchain
    block_data_database = ["White House pitches Biden's Covid bill as bipartisan — without Republican votes"]

    # mine each block and insert into the temporary blockchain
    block_number = 0
    for block_data in block_data_database:
        block_number += 1
        blockchain.mine_block(Block(block_data, block_number))

    # print each block out to the console
    for block in blockchain.blockchain:
        print(block)
    # check whether the blockchain is valid
    print(blockchain.is_blockchain_valid())


# only execute main() when this file is directly executed
if __name__ == '__main__':
    main()
