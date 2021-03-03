from web import mysql
from Blocks.Blockchain import Blockchain
from Blocks.Block import Block
from decimal import *


# custom exceptions for transaction errors
class InvalidTransactionException(Exception):
    pass


class InsufficientFundsException(Exception):
    pass


# what a mysql table looks like. Simplifies access to the database 'crypto'
class Table:
    # specify the table name and columns
    # EXAMPLE table:
    #                                   blockchain
    #
    # block_number    block_hash    block_previous_hash   block_data    block_nonce
    #   -data-          -data-             -data-           -data-         -data-
    #
    # EXAMPLE initialization: ...Table("blockchain", "block_number", "block_hash", "block_previous_hash", "block_data", "block_nonce")
    def __init__(self, table_name, *args):
        self.table = table_name
        self.columns = "({})".format(",".join(args))
        self.columnsList = args

        # if table does not already exist, create it.
        if is_new_table(table_name):
            create_data = ""
            for column in self.columnsList:
                create_data += "{} varchar(100),".format(column)

            cur = mysql.connection.cursor()  # create the table
            cur.execute("CREATE TABLE {}({})".format(self.table, create_data[:len(create_data) - 1]))
            cur.close()

    # get all the values from the table
    def get_all_rows(self):
        cur = mysql.connection.cursor()
        _result = cur.execute("SELECT * FROM {}".format(self.table))
        data = cur.fetchall()
        return data

    # get one value from the table based on a column's data
    # EXAMPLE using blockchain: ...get_one_row("hash","00003f73gh93...")
    def get_one_row(self, search, value):
        data = {}
        cur = mysql.connection.cursor()
        result = cur.execute(
            "SELECT * FROM {} WHERE {} = \"{}\"".format(self.table, search, value)
        )
        if result > 0:
            data = cur.fetchone()
        cur.close()
        return data

    @staticmethod
    def update_balance(candidate, balance, seek_method):
        cur = mysql.connection.cursor()
        if seek_method == "address":
            cur.execute(
                "UPDATE users SET balance = \"{}\" WHERE walletAddress = \"{}\"".format(balance, candidate)
            )
            mysql.connection.commit()
        elif seek_method == "username":
            cur.execute(
                "UPDATE users SET balance = \"{}\" WHERE username = \"{}\"".format(balance, candidate)
            )
            mysql.connection.commit()
        cur.close()

    # delete a value from the table based on column's data
    def delete_one_row(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE FROM {} where {} = \"{}\"".format(self.table, search, value)
        )
        mysql.connection.commit()
        cur.close()

    # delete all values from the table.
    @staticmethod
    def delete_all_rows(table_name):
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE FROM {}".format(table_name)
        )
        mysql.connection.commit()
        cur.close()

    # remove table from mysql
    """def drop_table(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE {}".format(self.table))
        cur.close()"""

    # insert values into the table
    def insert_row(self, *args):
        data = ""
        for arg in args:  # convert data into string mysql format
            data += "\"{}\",".format(arg)

        cur = mysql.connection.cursor()
        sql_string = "INSERT INTO {}{} VALUES({})".format(self.table, self.columns, data[:len(data) - 1])
        print(sql_string)
        cur.execute(sql_string)
        mysql.connection.commit()
        cur.close()


# execute mysql code
def execute_non_query(sql_string):
    cur = mysql.connection.cursor()
    cur.execute(sql_string)
    mysql.connection.commit()
    cur.close()


# check if table already exists
def is_new_table(table_name):
    cur = mysql.connection.cursor()

    try:  # attempt to get data from table
        _result = cur.execute("SELECT * from {}".format(table_name))
        cur.close()
    except:
        return True
    else:
        return False


# check if user already exists
def is_new_user(candidate, seek_method):
    # access the users table and get all values from column "username"
    users = Table("users", "username", "name", "email", "password", "walletAddress", "balance")
    data = users.get_all_rows()
    if seek_method == "username":
        usernames = [user.get('username') for user in data]
        return False if candidate in usernames else True
    elif seek_method == "address":
        addresses = [address.get('walletAddress') for address in data]
        return False if candidate in addresses else True


def is_address_unique(address):
    users_table = Table("users", "username", "name", "email", "password", "walletAddress", "balance")
    data = users_table.get_all_rows()
    addresses = [address.get('walletAddress') for address in data]
    print(addresses)

    return False if address in addresses else True


# send money from one user to another
def send_linkt(sender, recipient, amount):
    getcontext().prec = 12
    # verify that the amount is an integer or floating value
    try:
        amount = Decimal(amount)
    except ValueError:
        raise InvalidTransactionException("Amount of LinkT given is not a valid number.")

    # verify that the user has enough money to send (exception if it is the BANK)
    if sender == "BANK":
        # verify that the recipient exists
        if is_new_user(recipient, "address"):
            raise InvalidTransactionException("The Wallet Address You Are Trying to Send To Does Not Exist.")
        else:
            pass
    else:
        sender_balance = get_balance(sender, "address")
        recipient_balance = get_balance(recipient, "address")
        # verify that the recipient exists
        if is_new_user(recipient, "address"):
            raise InvalidTransactionException("The Wallet Address You Are Trying to Send To Does Not Exist.")
        # verify that the user is not sending money to themselves or amount is less than or 0
        if sender == recipient or amount <= 0.00:
            raise InvalidTransactionException("Invalid Transaction.")
        # verify that the user has enough funds
        if amount > sender_balance:
            raise InsufficientFundsException("Insufficient Funds.")

    # update the blockchain and sync to mysql
    blockchain = get_blockchain()
    block_number = len(blockchain.blockchain) + 1
    block_data = "{}-->{}-->{}".format(sender, recipient, amount)
    blockchain.mine_block(Block(block_number, block_data))

    users_table = Table("users", "username", "name", "email", "password", "walletAddress", "balance")
    # update sender balance
    users_table.update_balance(
        candidate=sender,
        balance=Decimal(sender_balance) - Decimal(amount),
        seek_method="address"
    )
    # update recipient balance
    users_table.update_balance(
        candidate=recipient,
        balance=Decimal(recipient_balance) + Decimal(amount),
        seek_method="address"
    )

    sync_blockchain(blockchain)


# get the balance of a user
def get_balance(candidate, seek_method):
    getcontext().prec = 12
    users_table = Table("users", "username", "name", "email", "password", "walletAddress", "balance")
    if seek_method == "address":
        user = users_table.get_one_row("walletAddress", candidate)
        return Decimal(user.get('balance'))
    elif seek_method == "username":
        user = users_table.get_one_row("username", candidate)
        return Decimal(user.get('balance'))


# get the blockchain from mysql and convert to Blockchain object
def get_blockchain():
    blockchain = Blockchain()
    blockchain_sql = Table(
        "blockchain",
        "block_number",
        "block_hash",
        "block_previous_hash",
        "block_data",
        "block_nonce"
    )
    for b in blockchain_sql.get_all_rows():
        blockchain.add_block(
            Block(
                int(b.get('block_number')),
                b.get('block_previous_hash'),
                b.get('block_data'),
                int(b.get('block_nonce'))
            )
        )

    return blockchain


# update blockchain in mysql table
def sync_blockchain(blockchain):
    blockchain_sql = Table(
        "blockchain",
        "block_number",
        "block_hash",
        "block_previous_hash",
        "block_data",
        "block_nonce"
    )
    blockchain_sql.delete_all_rows("blockchain")

    for block in blockchain.blockchain:
        blockchain_sql.insert_row(
            str(block.block_number),
            block.hash(),
            block.block_previous_hash,
            block.block_data,
            block.block_nonce
        )
