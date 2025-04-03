import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def db_connect():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'doctor_patient_system'),
    )