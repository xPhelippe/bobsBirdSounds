import csv
import os

# clear out files from previous runs
file = open('newConfig.yaml','w')
file.close()

file = open('failed.csv','w')
file.close()

file = open('success.csv','w')
file.close()

# all placeholders to be replaced
bird_name_placeholder = "<!<!bird_name!>!>"
bird_file_name_placeholder = "<!<!bird_file_name!>!>" # 2 of these
bird_proper_name_placeholder = "<!<!bird_proper_name!>!>"
bird_file_name_no_ext_placeholder = "<!<!bird_file_name_no_ext!>!>"

bird_name_source_file = "common_latin_bird_names.csv"

total_birds = 0
succeeded_birds = 0
failed_birds = 0

with open(bird_name_source_file,'r',encoding="utf-8") as sourceFile:

    reader = csv.reader(sourceFile)
    next(reader)  # Skip the header row

    for row in reader:
        total_birds = total_birds + 1

        common_name = row[0].replace("’","'")
        latin_name = row[1].replace(' ', '-')
        full_name = f"{common_name} ({latin_name})"

        print(f"Creating config for {full_name}")

        # create names 
        bird_name = common_name.replace("-", " ").replace ("'","").lower()
        bird_proper_name = common_name

        # find the folder for the bird
        bird_folder_search_name = common_name.replace("'","").replace(" ","-")
        base_path = "bird_noises\\"
        if os.path.exists(base_path + bird_folder_search_name):
            print(f"found folder for {common_name}")
        else:
            print(f"no folder found for {common_name}")
            with open("failed.csv","a",encoding="utf-8") as failedFile:
                failedFile.write(f"{common_name},{latin_name}\n")
            failed_birds = failed_birds + 1
            continue

        # find file in the folder
        files = os.listdir(base_path + bird_folder_search_name)
        if len(files) != 1:
            print(f"more than one file in this directory {base_path + bird_folder_search_name}")
            print("Please go check and see why")
            with open("failed.csv","a",encoding="utf-8") as failedFile:
                failedFile.write(f"{common_name},{latin_name}\n")
            failed_birds = failed_birds + 1
            continue
        else:
            bird_file_name = bird_folder_search_name + "/" + files[0]
            bird_file_name_no_ext = files[0].split("_")[0]

        # append to config file 
        with open('config.yaml','r',encoding='utf-8') as templateConfig:

            text = templateConfig.read()

            text = text.replace(bird_name_placeholder,bird_name)
            text = text.replace(bird_file_name_placeholder, bird_file_name)
            text = text.replace(bird_proper_name_placeholder, bird_proper_name)
            text = text.replace(bird_file_name_no_ext_placeholder, bird_file_name_no_ext)

            with open('newConfig.yaml','a',encoding="utf-8") as newConfig:
                newConfig.write(text)
        
        print(f"Successfully created config for {common_name}")
        with open("success.csv","a") as successFile:
                successFile.write(f"{common_name},{latin_name}\n")
        succeeded_birds = succeeded_birds + 1
    

print(f"successfully created config for {succeeded_birds}/{total_birds}")