import mysql.connector
import datetime

class MessMenu:
    def __init__(self, host: str, user: str, password: str, database: str):
        """Initialize the MessMenu class with database connection parameters."""
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def get_today_menu(self):
        """Fetch today's menu based on the current day of the week."""
        current_day = datetime.datetime.today().strftime('%A')

        query = "SELECT morning_menu, evening_menu, night_menu, dessert FROM menu WHERE day_of_week = %s"
        self.cursor.execute(query, (current_day,))
        menu_data = self.cursor.fetchone()

        if menu_data:
            morning_menu, evening_menu, night_menu, dessert = menu_data
            response = (f"Today's menu:\n"
                        f"Morning: {morning_menu}\n"
                        f"Evening: {evening_menu}\n"
                        f"Night: {night_menu}\n"
                        f"Dessert: {dessert}")
        else:
            response = "Menu not found for today."

        return response

    def get_specific_day_menu(self, day: str):
        """Fetch the menu for a specific day."""
        query = "SELECT morning_menu, evening_menu, night_menu, dessert FROM menu WHERE day_of_week = %s"
        self.cursor.execute(query, (day,))
        menu_data = self.cursor.fetchone()

        if menu_data:
            morning_menu, evening_menu, night_menu, dessert = menu_data
            response = (f"{day} menu:\n"
                        f"Morning: {morning_menu}\n"
                        f"Evening: {evening_menu}\n"
                        f"Night: {night_menu}\n"
                        f"Dessert: {dessert}")
        else:
            response = f"No menu found for {day}."

        return response

    def close_connection(self):
        """Close the database connection."""
        self.cursor.close()
        self.connection.close()
