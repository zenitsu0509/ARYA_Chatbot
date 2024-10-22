import mysql.connector
from mysql.connector import Error
from config import load_config
from datetime import datetime
from typing import Dict, List, Optional

class MessMenu:
    def __init__(self):
        self.config = load_config()
        self.meal_times = {
            'morning': (5, 10),    # 5 AM to 10 AM
            'evening': (11, 16),   # 11 AM to 4 PM
            'night': (17, 23)      # 5 PM to 11 PM
        }
    
    def connect_to_db(self):
        """Establish connection to the MySQL database using credentials from config."""
        try:
            connection = mysql.connector.connect(
                host="127.0.0.1",
                database="Mess_Menu",
                user=self.config['MYSQL_USER'],
                password=self.config['MYSQL_PASSWORD']
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def get_menu_for_day(self, day_of_week: str) -> Optional[Dict]:
        """Fetch the menu for a specific day."""
        connection = self.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = "SELECT * FROM menu WHERE day_of_week = %s"
                cursor.execute(query, (day_of_week,))
                result = cursor.fetchone()
                return result
            except Error as e:
                print(f"Error fetching menu for {day_of_week}: {e}")
                return None
            finally:
                cursor.close()
                connection.close()

    def get_full_week_menu(self) -> Optional[List[Dict]]:
        """Fetch the full menu for the week."""
        connection = self.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT * FROM menu 
                    ORDER BY FIELD(day_of_week, 
                        'Sunday', 'Monday', 'Tuesday', 'Wednesday', 
                        'Thursday', 'Friday', 'Saturday')
                """
                cursor.execute(query)
                result = cursor.fetchall()
                return result
            except Error as e:
                print(f"Error fetching weekly menu: {e}")
                return None
            finally:
                cursor.close()
                connection.close()

    def get_current_meal_time(self) -> str:
        """Determine current meal time based on hour of day."""
        current_hour = datetime.now().hour
        
        for meal_type, (start_hour, end_hour) in self.meal_times.items():
            if start_hour <= current_hour <= end_hour:
                return meal_type
        return 'morning'  # Default to morning menu during off-hours

    def get_current_menu(self) -> str:
        """Get and format the current day's menu based on time."""
        current_time = datetime.now()
        current_day = current_time.strftime('%A')
        current_meal = self.get_current_meal_time()
        
        menu_data = self.get_menu_for_day(current_day)
        if not menu_data:
            return "Menu not available."

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

        return "\n".join(response)

    def format_full_menu(self, data: List[Dict]) -> str:
        """Format the full week menu for display."""
        if not data:
            return "Menu not available."
            
        response = ["📅 Full Week Menu 📅\n"]
        
        for day_menu in data:
            response.append(f"=== {day_menu['day_of_week']} ===")
            response.append(f"🌅 Breakfast: {day_menu['morning_menu']}")
            response.append(f"🌞 Lunch: {day_menu['evening_menu']}")
            
            if day_menu['night_menu'] == 'OFF':
                response.append("🌙 Dinner: Mess Closed")
            else:
                response.append(f"🌙 Dinner: {day_menu['night_menu']}")
                
            if day_menu['dessert'] != 'OFF':
                response.append(f"🍨 Dessert: {day_menu['dessert']}")
            
            response.append("")  # Empty line between days
            
        return "\n".join(response)

def main():
    menu_system = MessMenu()
    
    # Example 1: Get current menu based on time
    print("\nCurrent Menu:")
    print("-" * 50)
    print(menu_system.get_current_menu())
    
    # Example 2: Get full week menu
    print("\nFull Week Menu:")
    print("-" * 50)
    weekly_menu = menu_system.get_full_week_menu()
    if weekly_menu:
        print(menu_system.format_full_menu(weekly_menu))

if __name__ == "__main__":
    main()