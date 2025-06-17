from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# SQL Server connection
sql_conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=vamsidb.c9uqkcqc8c92.ap-south-1.rds.amazonaws.com;'
    'DATABASE=test01;'
    'UID=admin;'
    'PWD=Svamsi79955;'
    'TrustServerCertificate=yes;'
)
sql_cursor = sql_conn.cursor()

# Create SQL table if not exists
sql_cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
    CREATE TABLE Users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255),
        email NVARCHAR(255),
        password NVARCHAR(255),
        phone NVARCHAR(20)
    );
""")
sql_conn.commit()

# MongoDB connection
mongo_client = MongoClient("mongodb+srv://Rachana2003:Rachana2003@cluster0.yktllua.mongodb.net/")
mongo_db = mongo_client["formdata"]
mongo_col = mongo_db["submissions"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    phone = request.form.get('phonenumber')
    email = request.form.get('email')
    address = request.form.get('address')
    comments = request.form.get('Comments')
    password = request.form.get('password')

    # Insert into SQL Server
    sql_cursor.execute("INSERT INTO Users (name, email, password, phone) VALUES (?, ?, ?, ?)",
                       (name, email, password, phone))
    sql_conn.commit()

    # Get inserted SQL ID
    sql_cursor.execute("SELECT TOP 1 id FROM Users ORDER BY id DESC")
    latest_id = sql_cursor.fetchone()[0]

    # Insert into MongoDB
    mongo_col.insert_one({
        "sql_id": latest_id,
        "address": address,
        "comments": comments,
        "rm": datetime.utcnow()
    })

    # Fetch ALL users
    sql_cursor.execute("SELECT * FROM Users")
    all_user_data = sql_cursor.fetchall()

    # Fetch all corresponding MongoDB data
    mongo_docs = list(mongo_col.find({}))

    # Create dictionary for fast lookup of Mongo docs by sql_id, only if sql_id exists
    mongo_dict = {doc["sql_id"]: doc for doc in mongo_docs if "sql_id" in doc}



    return render_template('submitteddata.html', users=all_user_data, mongo_dict=mongo_dict)

@app.route('/get-data', methods=['GET', 'POST'])
def get_data():
    if request.method == 'POST':
        input_id = request.form.get('input_id')
        if input_id and input_id.isdigit():
            input_id_int = int(input_id)

            # Query SQL Server for user
            sql_cursor.execute("SELECT * FROM Users WHERE id = ?", (input_id_int,))
            user = sql_cursor.fetchone()

            # Query MongoDB for matching data (optional)
            mongo = None
            if user:
                mongo = mongo_col.find_one({"sql_id": input_id_int})

            # Render template with `user` and `mongo`
            return render_template('data.html', user=user, mongo=mongo)
        else:
            # Invalid input ID (non-numeric)
            return render_template('data.html', user=None, mongo=None, message="Please enter a valid numeric ID.")

    # GET request
    return render_template('get_data.html')

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_data(id):
    if request.method == 'POST':
        sql_cursor.execute("DELETE FROM Users WHERE id = ?", (id,))
        sql_conn.commit()
        mongo_col.delete_one({"sql_id": id})
        return redirect(url_for('get_data'))
    return render_template('delete.html', id=id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
