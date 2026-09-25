import os
from dotenv import load_dotenv
import mysql.connector

from mysql.connector import errorcode
load_dotenv()

def create_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def add_customer(full_name, address, phone_number, user_id, email, password):
    conn_obj = create_connection()
    cur_obj = conn_obj.cursor()
    sql = """
        INSERT INTO cust_details 
        (full_name, address, phone_number, user_id, email, password) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (full_name, address, phone_number, user_id, email, password)

    try:
        cur_obj.execute(sql, values)
        conn_obj.commit()
        print("Customer added successfully")
        return True
    except mysql.connector.Error as err:
        print("Error: {}".format(err))
        conn_obj.rollback()
        print("Error inserting customer", err)
        return False
    finally:
        cur_obj.close()
        conn_obj.close()

#add_customer("Test User", "Kolkata", "9876543210", "testuser", "test@example.com","TestPassword123")

def user_id_exists(user_id):
    conn_obj = create_connection()
    cur_obj = conn_obj.cursor()

    sql = """
            SELECT cust_id
            FROM cust_details
            WHERE user_id = %s
        """

    cur_obj.execute(sql, (user_id,))

    result = cur_obj.fetchone()

    cur_obj.close()
    conn_obj.close()

    return result is not None

def email_exists(email):
    conn_obj = create_connection()
    cur_obj = conn_obj.cursor()

    sql = """
        SELECT cust_id
        FROM cust_details
        WHERE email = %s
    """

    cur_obj.execute(sql, (email,))

    result = cur_obj.fetchone()

    cur_obj.close()
    conn_obj.close()

    return result is not None

sql = "SELECT * FROM cust_details"
conn_obj = create_connection()
cur_obj = conn_obj.cursor()
cur_obj.execute(sql)

print("Result = ", cur_obj.fetchall())


print(user_id_exists("testuser"))
print(user_id_exists("somethingelse"))