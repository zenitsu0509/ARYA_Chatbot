import mysql.connector
from mysql.connector import Error
from config import load_config

def connect_to_db():
    """Establish connection to the MySQL database using credentials from config."""
    config = load_config()  # Load the configuration

    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",  # Assuming you're using localhost; modify if necessary
            database="Mess_Menu",
            user=config['MYSQL_USER'],       # Loaded from config
            password=config['MYSQL_PASSWORD'] # Loaded from config
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_menu_for_day(day_of_week):
    """Fetch the menu for a specific day."""
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM menu WHERE day_of_week = %s"
            cursor.execute(query, (day_of_week,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result
        except Error as e:
            print(f"Error fetching menu for {day_of_week}: {e}")
            return None

def get_full_week_menu():
    """Fetch the full menu for the week."""
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM menu"
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            connection.close()
            return result
        except Error as e:
            print(f"Error fetching weekly menu: {e}")
            return None
