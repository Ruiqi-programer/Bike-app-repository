import schedule
import time
from GetDataFromOpenWeather import get_weather

schedule.every(1).hours.do(get_weather)

while True:
    schedule.run_pending()
    time.sleep(1)
