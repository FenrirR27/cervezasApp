from flask import Flask, render_template, request, session, redirect, url_for
import config
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

app.config['MYSQL_HOST'] = config.HOST
app.config['MYSQL_USER'] = config.USERNAME
app.config['MYSQL_PASSWORD'] = config.PASSWORD
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MYSQL_DB'] = config.DATABASE
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_PORT'] = 3306
app.config["MYSQL_CUSTOM_OPTIONS"] = {"autocommit": True, "charset": "utf8mb4", "ssl": False}

mysql = MySQL(app)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()

    if user is not None:
        session['email'] = email
        session['name'] = user['name']

        return redirect(url_for('beers'))
    else:
        return render_template('index.html', message="Las credenciales no son correctas")


@app.route('/beers', methods=['GET'])
def beers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM beers")
    beers = cur.fetchall()

    return render_template('beers.html', beers=beers)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/new-beer', methods=['POST'])
def newBeer():
    name = request.form['name']
    style = request.form['style']
    description = request.form['description']
    email = session['email']
    d = datetime.now()
    dateAdded = d.strftime("%Y-%m-%d %H:%M:%S")

    if name and style and description and email:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO beers ( name, style, description, date_added) VALUES ( %s, %s, %s, %s)"
        data = ( name, style, description, dateAdded)
        cur.execute(sql, data)
        cur.close()
        mysql.connection.commit()

    return redirect(url_for('beers'))


@app.route('/delete-beer', methods=['POST'])
def deleteBeer():
    cur = mysql.connection.cursor()
    id = request.form['id']
    sql = "DELETE FROM beers WHERE id = %s"
    data = (id,)
    cur.execute(sql, data)
    cur.close()
    mysql.connection.commit()

    return redirect(url_for('beers'))


if __name__ == '__main__':
    app.run(debug=True)
