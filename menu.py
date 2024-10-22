import mysql.connector
from mysql.connector import Error
from config import load_config
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MessMenu:
    def __init__(self):
        logger.debug("Initializing MessMenu")
        self.config = load_config()
        logger.debug(f"Database config loaded: host={self.config.get('MYSQL_HOST')}, user={self.config.get('MYSQL_USER')}, database={self.config.get('MYSQL_DATABASE')}")
        self.meal_times = {
            'morning': (5, 10),    # 5 AM to 10 AM
            'evening': (11, 16),   # 11 AM to 4 PM
            'night': (17, 23)      # 5 PM to 11 PM
        }
    
    def connect_to_db(self):
        """Establish connection to the MySQL database using credentials from config."""
        try:
            logger.debug("Attempting to connect to database...")
            connection = mysql.connector.connect(
                host=self.config.get('MYSQL_HOST', '127.0.0.1'),
                database=self.config.get('MYSQL_DATABASE', 'Mess_Menu'),
                user=self.config['MYSQL_USER'],
                password=self.config['MYSQL_PASSWORD'],
                port=self.config.get('MYSQL_PORT', 3306)
            )
            if connection.is_connected():
                db_info = connection.get_server_info()
                logger.debug(f"Successfully connected to MySQL Server version {db_info}")
                cursor = connection.cursor()
                cursor.execute("select database();")
                db_name = cursor.fetchone()[0]
                logger.debug(f"Connected to database: {db_name}")
                cursor.close()
                return connection
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise Exception(f"Database connection failed: {str(e)}")

    def get_menu_for_day(self, day_of_week: str) -> Optional[Dict]:
        """Fetch the menu for a specific day."""
        logger.debug(f"Fetching menu for {day_of_week}")
        connection = None
        cursor = None
        try:
            connection = self.connect_to_db()
            if not connection:
                logger.error("Failed to establish database connection")
                return None

            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM menu WHERE day_of_week = %s"
            logger.debug(f"Executing query: {query} with day: {day_of_week}")
            
            cursor.execute(query, (day_of_week,))
            result = cursor.fetchone()
            
            if result:
                logger.debug(f"Menu found for {day_of_week}: {result}")
            else:
                logger.debug(f"No menu found for {day_of_week}")
            
            return result

        except Error as e:
            logger.error(f"Error fetching menu for {day_of_week}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                logger.debug("Database connection closed")

    def get_full_week_menu(self) -> Optional[List[Dict]]:
        """Fetch the full menu for the week."""
        logger.debug("Fetching full week menu")
        connection = None
        cursor = None
        try:
            connection = self.connect_to_db()
            if not connection:
                logger.error("Failed to establish database connection")
                return None

            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT * FROM menu 
                ORDER BY FIELD(day_of_week, 
                    'Sunday', 'Monday', 'Tuesday', 'Wednesday', 
                    'Thursday', 'Friday', 'Saturday')
            """
            logger.debug(f"Executing query: {query}")
            
            cursor.execute(query)
            result = cursor.fetchall()
            
            logger.debug(f"Retrieved {len(result) if result else 0} days of menu data")
            return result

        except Error as e:
            logger.error(f"Error fetching weekly menu: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                logger.debug("Database connection closed")

    def get_current_menu(self) -> str:
        """Get and format the current day's menu based on time."""
        logger.debug("Getting current menu")
        current_time = datetime.now()
        current_day = current_time.strftime('%A')
        current_meal = self.get_current_meal_time()
        
        logger.debug(f"Current day: {current_day}, Current meal time: {current_meal}")
        
        menu_data = self.get_menu_for_day(current_day)
        if not menu_data:
            logger.error("Failed to retrieve menu data")
            return "Sorry, I couldn't retrieve the menu at the moment."

        meal_map = {
            'morning': ('morning_menu', '🌅 Breakfast'),
            'evening': ('evening_menu', '🌞 Lunch'),
            'night': ('night_menu', '🌙 Dinner')
        }

        menu_key, meal_title = meal_map[current_meal]
        
        response = [
            f"🕐 Current Time: {current_time.strftime('%I:%M %p')}",
            f"📅 {current_day}'s Menu\n",
            f"{meal_title}:",
            f"{menu_data[menu_key]}"
        ]

        if menu_data['dessert'] != 'OFF' and current_meal in ['evening', 'night']:
            response.append(f"\n🍨 Dessert: {menu_data['dessert']}")

        final_response = "\n".join(response)
        logger.debug(f"Generated menu response: {final_response}")
        return final_response

    def get_current_meal_time(self) -> str:
        """Determine current meal time based on hour of day."""
        current_hour = datetime.now().hour
        logger.debug(f"Current hour: {current_hour}")
        
        for meal_type, (start_hour, end_hour) in self.meal_times.items():
            if start_hour <= current_hour <= end_hour:
                logger.debug(f"Current meal time: {meal_type}")
                return meal_type
        
        logger.debug("Outside regular meal times, defaulting to morning")
        return 'morning'