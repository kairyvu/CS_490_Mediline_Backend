from flaskr.database import db_connect
from flask import jsonify

def get_tables():
    con = db_connect()
    cursor = con.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    cursor.close()
    con.close()
    tables_names = [table[0] for table in tables]
    return jsonify({"tables": tables_names}), 200
