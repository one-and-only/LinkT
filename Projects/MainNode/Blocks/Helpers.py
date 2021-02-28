from hashlib import sha512


class Helpers:
    # create a hash with the given data
    def update_hash(*args):
        # initialize hashing_text and the algorithm (SHA-512)
        hashing_text = ""
        block_hash = sha512()  # initialize the block hash
        for arg in args:
            hashing_text += str(arg)  # set the hash string of the block

        block_hash.update(hashing_text.encode('utf-8'))  # set the correct block hash string
        return block_hash.hexdigest()  # return the hex block hash
