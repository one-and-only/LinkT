# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha512_crypt
from flask_mysqldb import MySQL
from Web.config import Config
from Web.Pages import index

app = Flask(__name__)

# configure the app
appconfig = Config()
app.config['MYSQL_HOST'] = appconfig.mysql_host
app.config['MYSQL_USER'] = appconfig.mysql_user
app.config['MYSQL_PASSWORD'] = appconfig.mysql_password
app.config['MYSQL_DB'] = appconfig.mysql_db
app.config['MYSQL_PORT'] = appconfig.mysql_port
app.config['MYSQL_CURSORCLASS'] = appconfig.mysql_cursorclass

mysql = MySQL(app)


# use def_page_name as the function name to initialize pages here
# use @app.route("page_url") to set the page for each URL
@app.route("/")
def def_index_page():
    return render_template('index.html')  # Show the index page to the user


if __name__ == '__main__':
    app.secret_key = appconfig.app_secret
    app.run(debug=True)
