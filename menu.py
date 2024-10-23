from datetime import datetime
import pandas as pd
import logging
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MessMenu:
    def __init__(self):
        logger.debug("Initializing MessMenu")
        # Read CSV file into DataFrame
        self.df = pd.read_csv('data\mess_menu.csv')
        self.meal_times = {
            'morning': (5, 10),    # 5 AM to 10 AM
            'evening': (11, 16),   # 11 AM to 4 PM
            'night': (17, 23)      # 5 PM to 11 PM
        }
        logger.debug(f"Loaded menu data with {len(self.df)} rows")
    
    def get_menu_for_day(self, day_of_week: str) -> Optional[Dict]:
        """Fetch the menu for a specific day."""
        logger.debug(f"Fetching menu for {day_of_week}")
        try:
            # Filter DataFrame for the specific day
            menu = self.df[self.df['day_of_week'] == day_of_week]
            
            if not menu.empty:
                # Convert the row to dictionary
                result = menu.iloc[0].to_dict()
                logger.debug(f"Menu found for {day_of_week}: {result}")
                return result
            else:
                logger.debug(f"No menu found for {day_of_week}")
                return None

        except Exception as e:
            logger.error(f"Error fetching menu for {day_of_week}: {e}")
            return None

    def get_full_week_menu(self) -> Optional[List[Dict]]:
        """Fetch the full menu for the week."""
        logger.debug("Fetching full week menu")
        try:
            # Define the correct order of days
            day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 
                        'Thursday', 'Friday', 'Saturday']
            
            # Sort DataFrame according to day order
            sorted_df = self.df.set_index('day_of_week').loc[day_order].reset_index()
            
            # Convert DataFrame to list of dictionaries
            result = sorted_df.to_dict('records')
            
            logger.debug(f"Retrieved {len(result)} days of menu data")
            return result

        except Exception as e:
            logger.error(f"Error fetching weekly menu: {e}")
            return None

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