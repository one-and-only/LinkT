# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import pbkdf2_sha512
from flask_mysqldb import MySQL
from functools import wraps
from Web.config import Config
from Web.mysql import *
from forms import *
import random
import string

app = Flask(__name__)

# configure the app
"""
NOTE: Since most of the configuration is sensitive information,
it is stored in a separate configuration file, which is ignored 
by git (through the .gitignore). All values in the app.config[''] 
fields can be set with your own values if you want to host this site.
"""
appconfig = Config()
app.config['MYSQL_HOST'] = appconfig.mysql_host
app.config['MYSQL_USER'] = appconfig.mysql_user
app.config['MYSQL_PASSWORD'] = appconfig.mysql_password
app.config['MYSQL_DB'] = appconfig.mysql_db
app.config['MYSQL_PORT'] = appconfig.mysql_port
app.config['MYSQL_CURSORCLASS'] = appconfig.mysql_cursorclass

mysql = MySQL(app)


def create_address():
    address_candidate = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))

    if is_address_unique(address_candidate):
        return address_candidate
    else:
        create_address()


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please login before using this page.", "danger")
            return redirect(url_for('login'))

    return wrap


def is_not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            flash("You are already logged in!", "danger")
            return redirect(url_for('dashboard'))

    return wrap


def log_in_user(username):
    users_table = Table("users", "username", "name", "email", "password", "walletAddress", "balance")
    user = users_table.get_one_row("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')
    session['walletAddress'] = user.get('walletAddress')


def is_correct_password(password, password_hash):
    return pbkdf2_sha512.verify(password, password_hash)


# use page_name as the function name to initialize pages here
# use @app.route("page_url") to set the page for each URL
@app.route("/")
def index():
    return render_template('index.html', title='Home | LinkT')  # Show the page to the user


@app.route("/dashboard")
@is_logged_in
def dashboard():
    return render_template('dashboard.html', title='Dashboard | LinkT', session=session)


@app.route("/register", methods=['GET', 'POST'])
def register():
    register_form = RegisterForm(request.form)
    users_table = Table("users", "username", "name", "email", "password", "walletAddress", "balance")

    if request.method == "POST" and register_form.validate():
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        wallet_address = create_address()

        if is_new_user(username, "username"):
            if username != "BANK":
                password_encrypted = pbkdf2_sha512.hash(register_form.password.data)
                users_table.insert_row(username, name, email, password_encrypted, wallet_address, "0." + "0" * 12)
                log_in_user(username)
                return redirect(url_for('dashboard'))
            else:
                flash("The username \"BANK\" is reserved.", "danger")
        else:
            flash('User Already Exists!', 'danger')
            return redirect(url_for('register'))
    elif request.method == "POST" and not register_form.validate():
        flash('Invalid Data. Please make sure that you entered your data correctly and your passwords match', 'danger')
        return redirect(url_for('register'))

    return render_template('register.html', title='Sign Up | LinkT', form=register_form)


@app.route("/login", methods=['GET', 'POST'])
@is_not_logged_in
def login():
    if request.method == "POST":
        username = request.form['username']
        password_candidate = request.form['password']

        users_table = Table("users", "username", "name", "email", "password", "walletAddress", "balance")
        user = users_table.get_one_row("username", username)
        password_hash = user.get('password')

        if password_hash is None:
            flash("Invalid Username or Password", 'danger')
            return redirect(url_for('login'))
        else:
            if is_correct_password(password_candidate, password_hash):
                log_in_user(username)
                flash("You are now logged in.", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid Username or Password", 'danger')
                return redirect(url_for('login'))

    return render_template('login.html', title="Login | LinkT")


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("You have logged out", "success")
    return redirect(url_for('login'))


@app.route('/send', methods=['GET', 'POST'])
@is_logged_in
def send():
    form = SendLinkTForm(request.form)
    balance = get_balance(session.get('username'), "username")

    if request.method == "POST":
        try:
            send_linkt(
                sender=session.get("walletAddress"),
                recipient=request.form['recipientAddress'],
                amount=request.form['amount']
            )

            flash("LinkT has been sent!", "success")
        except Exception as e:
            flash(str(e), "danger")

        return redirect(url_for('send'))

    return render_template('send.html', balance=balance, form=form)


if __name__ == '__main__':
    app.secret_key = appconfig.app_secret
    app.run(debug=True, host='0.0.0.0', port='5000')
