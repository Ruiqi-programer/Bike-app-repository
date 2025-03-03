
####################DOWNLOAD from JCDECAUX###############
# import dbinfo
import requests
import traceback
import datetime
import time
import os
import sys
import json

API_KEY = "a39626f86048c97dbd2da2d0c5b7e67d"  
lat=53.3498
lon=-6.2603
part="minutely,alerts"
URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API_KEY}"


# Will be used to store text in a file
def write_to_file(text):

    # I first need to create a folder data where the files will be stored.
    if not os.path.exists('weather_data'):
        os.mkdir('weather_data')
        print("Folder 'weather_data' created!")
    else:
        print("Folder 'weather_data' already exists.")

    # now is a variable from datetime, which will go in {}.
    # replace is replacing white spaces with underscores in the file names

    # now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # filename=f"weather_data/weather_{now}.json"
    # with open(filename, "w",encoding="utf-8") as f:
    #     f.write(text)
    # print(f"数据存储到 {filename}")


def main():
    while True:
        try:
            r = requests.get(URL)
            print("API response status:", r.status_code)
            
            if r.status_code == 200:
                write_to_file(r.text)
                
                #格式化json文件，使其更可读
                data = json.loads(r.text)
                with open("test2.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
            else:
                print("API request failed:", r.status_code)

            time.sleep(5*60)
            
        except KeyboardInterrupt:
            print("\nmannually kill the program")
            sys.exit(0)
        except:
            print(traceback.format_exc())

# CTRL + Z to stop it
main()    