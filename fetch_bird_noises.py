import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import requests

# locations of elements in each row
DURATION = 2
SOUND_URL = 11

# CSV file with bird names
csv_file = 'common_latin_bird_names.csv'

# Initialize the Selenium WebDriver
driver = webdriver.Chrome()

def convert_time_string_to_second(time_string: str):
    # string looks like 0:36, 2:35, 5:09, etc

    minutes, seconds = time_string.split(":")

    minutes = int(minutes)
    seconds = int(seconds)

    return int(minutes * 60 + seconds)
    

# Function to search for bird sounds on xeno-canto.org
def search_bird_sounds(bird_name):
    try:
        driver.get(f'https://www.xeno-canto.org/species/{bird_name}')
    except Exception as e:
        print(f"Could not find a page for {bird_name}")
        return []

    try:
        table = driver.find_element(By.CLASS_NAME, 'results')
        rows = table.find_elements(By.TAG_NAME, 'tr')
    except:
        print("bird not found")
        return []

    download_urls = []
    download_urls_found = 0

    

    for idx, row in enumerate(rows):
        # skip header row
        if idx == 0:
            continue

        # Iterate through cells of each row
        cells = row.find_elements(By.TAG_NAME, 'td')
        cell_array = []
        for cell_idx, cell in enumerate(cells):
            cell_array.append(cell)

        # see if time duration is between 20s and 2min
        duration = cell_array[DURATION]
        # print(duration.text)
        seconds = convert_time_string_to_second(duration.text)

        if seconds > 20 and seconds < 120:
            # fetch download url
            download_element = cell_array[SOUND_URL]
            download_url = download_element.find_elements(By.TAG_NAME,"a")[0].get_attribute('href')
            # print(f"download url: {download_url}")

            download_urls.append(download_url)
            download_urls_found = download_urls_found + 1
        
        if download_urls_found >=5:
            break
    
    print(f"found {download_urls_found} eligible download urls for {bird_name}")
    return download_urls


        

    time.sleep(3)  # Wait for the page to load

    # Find the first result and get the audio URL
    # try:
    #     first_result = driver.find_element(By.CSS_SELECTOR, '.results .jp-type-single')
    #     audio_url = first_result.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
    #     return audio_url
    # except Exception as e:
    #     print(f"Could not find audio for {bird_name}: {e}")
    #     return None

# Read the CSV file and search for each bird

def download_file_to_folder(parent_folder, folder_name, file_url, file_name):
    
    folder_name = str(folder_name).replace("'","").replace(" ","-").replace("’","")
    file_name = str(file_name).replace("'","").replace(" ","-").replace("’","")
    
    # Create the full path to the folder
    folder_path = os.path.join(parent_folder, folder_name)
    
    # Check if the folder exists, and create it if it doesn't
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")
    
    # Download the file
    response = requests.get(file_url)
    
    # Save the file to the folder
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)

with open(csv_file, 'r',encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    i = 0

    successful_downloads = 0
    total_attempts = 0
    failed_birds = []
    successful_birds = []

    for row in reader:
        total_attempts = total_attempts + 1

        i = i + 1

        # if i > 5:
        #     break
        
        # fetch the names of the bird
        common_name = row[0].replace("’","'")
        latin_name = row[1].replace(' ', '-')
        bird_name = f"{common_name} ({latin_name})"

        # scrape the web page for the bird
        print(f"searching for the bird soud for {bird_name}")
        audio_urls = search_bird_sounds(latin_name)

        try: 
            # download the sounds from all the urls
            print("Downloading urls")
            if audio_urls:
                print(f"{common_name}: {audio_urls}")
                for idx, url in enumerate(audio_urls):
                    download_file_to_folder(
                        parent_folder="C:\\users\\souza\\Desktop\\bird_noises\\bird_noises",
                        folder_name=common_name,
                        file_name=f"{common_name}_{idx}.mp3",
                        file_url=url)
                
                print("downloaded all urls")
                successful_downloads = successful_downloads + 1
                successful_birds.append({
                    "common_name": common_name,
                    "latin_name": latin_name
                })
                with open("success.csv","a") as file:
                    file.write(f"{common_name},{latin_name}\n")

            else: 
                print(f"Could not find any urls for {common_name}")
                failed_birds.append({
                    "common_name": common_name,
                    "latin_name": latin_name
                })
                with open("failed.csv","a") as file:
                    file.write(f"{common_name},{latin_name}\n")
        except Exception as e:
            print(f"Failed to download for {bird_name}")
            print(e)
            failed_birds.append({
                "common_name": common_name,
                "latin_name": latin_name
            })
            with open("failed.csv","a") as file:
                    file.write(f"{common_name},{latin_name}\n")


    print(f"successfully downloaded {successful_downloads}/{total_attempts} birds")


    print("failed birds:")
    print(failed_birds)
    print("successful birds:")
    print(successful_birds)
    

# Close the WebDriver
driver.quit()
