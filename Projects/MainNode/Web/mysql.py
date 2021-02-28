from web import mysql, session
from Blocks.Blockchain import Blockchain
from Blocks.Block import Block


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
    # block_number    block_hash    block_previous_hash   block_data    block_nonce
    #   -data-          -data-             -data-           -data-         -data-
    #
    # EXAMPLE initialization: ...Table("blockchain", "number", "hash", "previous", "data", "nonce")
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

    # delete a value from the table based on column's data
    def delete_one_row(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE from {} where {} = \"{}\"".format(self.table, search, value)
        )
        mysql.connection.commit()
        cur.close()

    # delete all values from the table.
    def delete_all_rows(self):
        self.drop_table()  # remove table and recreate
        self.__init__(self.table, *self.columnsList)

    # remove table from mysql
    def drop_table(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE {}".format(self.table))
        cur.close()

    # insert values into the table
    def insert_row(self, *args):
        data = ""
        for arg in args:  # convert data into string mysql format
            data += "\"{}\",".format(arg)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO {}{} VALUES({})".format(self.table, self.columns, data[:len(data) - 1]))
        mysql.connection.commit()
        cur.close()


# execute mysql code from python
def execute_non_query(execution):
    cur = mysql.connection.cursor()
    cur.execute(execution)
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
def is_new_user(username):
    # access the users table and get all values from column "username"
    users = Table("users", "name", "email", "username", "password")
    data = users.get_all_rows()
    usernames = [user.get('username') for user in data]

    return False if username in usernames else True


# send money from one user to another
def send_money(sender, recipient, amount):
    # verify that the amount is an integer or floating value
    try:
        amount = float(amount)
    except ValueError:
        raise InvalidTransactionException("Invalid Transaction.")

    # verify that the user has enough money to send (exception if it is the BANK)
    if amount > get_balance(sender) and sender != "BANK":
        raise InsufficientFundsException("Insufficient Funds.")

    # verify that the user is not sending money to themselves or amount is less than or 0
    elif sender == recipient or amount <= 0.00:
        raise InvalidTransactionException("Invalid Transaction.")

    # verify that the recipient exists
    elif is_new_user(recipient):
        raise InvalidTransactionException("User Does Not Exist.")

    # update the blockchain and sync to mysql
    blockchain = get_blockchain()
    block_number = len(blockchain.blockchain) + 1
    block_data = "{}-->{}-->{}".format(sender, recipient, amount)
    blockchain.mine_block(Block(block_number, Block(block_data, block_number)))
    sync_blockchain(blockchain)


# get the balance of a user
def get_balance(username):
    balance = 0.00
    blockchain = get_blockchain()

    # loop through the blockchain and update balance
    for block in blockchain.blockchain:
        data = block.data.split("-->")
        if username == data[0]:
            balance -= float(data[2])
        elif username == data[1]:
            balance += float(data[2])
    return balance


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
    blockchain_sql.delete_all_rows()

    for block in blockchain.blockchain:
        blockchain_sql.insert_row(
            str(block.block_number),
            block.hash(),
            block.block_previous_hash,
            block.block_data,
            block.block_nonce
        )
