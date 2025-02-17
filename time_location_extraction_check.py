import os
import re
from datetime import datetime
import json
import glob
import pandas as pd

tasks = ["arbeit"]
GERMAN_MONTHS = {
    "Jan": "01", "Feb": "02", "Mär": "03", "Apr": "04", "Mai": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Okt": "10", "Nov": "11", "Dez": "12",
    "Jän": "01" 
}
for task in tasks:
    if not os.path.exists(f"{task}/"):
        os.makedirs(f"{task}/")
        
def date_extraction(folder_path,task):
    extracted_dates = []

    for file in os.listdir(folder_path):
        date = None
        
        if file.endswith(".txt"):
            with open(os.path.join(folder_path, "news__zeit_de_n_1_mann-repariert-holzvergaser-lebensgefaehrlich-verletzt_0.txt"), 'r', encoding='utf-8') as f:
                text = f.read()

            # Check for date format like 30.12.24 or 30.12.2024
            match1 = re.search(r'\b(\d{2})\.(\d{2})\.(\d{2})\b', text)
            match2 = re.search(r'\b(\d{2})\.(\d{2})\.(\d{4})\b', text)
            if match1:
                date = f"20{match1.group(3)}-{match1.group(2)}-{match1.group(1)}"
            elif match2:
                date = f"{match2.group(3)}-{match2.group(2)}-{match2.group(1)}"
            
            else:
                # Check for German month names
                for month, month_number in GERMAN_MONTHS.items():
                    match = re.search(rf'(\d{{1,2}})\s*\.?\s*{month}\w*\s*(\d{{4}})?', text)
                    if match:
                        day = match.group(1).zfill(2)
                        year = match.group(2) if match.group(2) else "2025"
                        date = f"{year}-{month_number}-{day}"
                        break

            # Extract date from the file name 
            if file not in extracted_dates:
                match = re.search(r'(\d{4})-(\d{2})-(\d{2})\.txt$', file)
                if match:
                    date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

            if 'date' in locals():
                extracted_dates.append({
                    "File": file,
                    "Date": date
                })

    with open(f'{task}/date_extracted.json', 'w', encoding='utf-8') as json_file:
        json.dump(extracted_dates, json_file, ensure_ascii=False, indent=4)

def find_city_in_text(text):  
    words = text.replace(',','').replace('.','').replace('(','').replace(')','').replace("'",'').replace('"','').lower().split()  
    for bundesland, cities in bundesland_cities.items():  
        for city in cities:  
            if city.lower() in words:  
                return bundesland, city  
    return None, None  

          
with open("bundesland_cities.json", "r", encoding="utf-8") as file:
    bundesland_cities = json.load(file)
    

def location_extraction(folder_path,task):
    matches = []

    for file in glob.glob(f"{folder_path}/*.txt"):
        file_name = os.path.basename(file)
        #title = file_name.rsplit('/')[-1].split('.')[0]

        try:
            content = open(file, 'r', encoding='utf-8').read()
            print(content)
        except Exception as e:
            print(f"Error reading file {file_name}: {e}")
            continue

        if content:
            bundesland, city = find_city_in_text(content)
            if city:
                matches.append({
                    "File": file_name,
                    "City": city,
                    "Bundesland": bundesland,
                    "Text": content 
                })
    with open(f'{task}/locations_extracted.json', 'w', encoding='utf-8') as json_file:
        json.dump(matches, json_file, ensure_ascii=False, indent=4)


def combine_json_files(date_file, location_file, output_file):
    with open(date_file, 'r', encoding='utf-8') as f1, open(location_file, 'r', encoding='utf-8') as f2:
        dates = {item['File']: item['Date'] for item in json.load(f1)}
        locations = json.load(f2)

    combined = []
    for loc in locations:
        if loc['File'] in dates:
            loc['Date'] = dates[loc['File']]
            combined.append(loc)

    with open(output_file, 'w', encoding='utf-8') as out:
        json.dump(combined, out, ensure_ascii=False, indent=4)


def json_to_excel(json_file, excel_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["Date", "City"])  

    df.to_excel(excel_file, index=False, columns=["Date", "City", "Bundesland", "File", "Text"])


def main():
    for task in tasks:
        folder_path ="check" + task + "/"
        #date_extraction(folder_path,task)
        location_extraction(folder_path,task)
        combine_json_files(f'{task}/date_extracted.json',f'{task}/locations_extracted.json',f'{task}/output.json')
        # json_to_excel(f'{task}/output.json',f'{task}/output.xlsx')

if __name__ == "__main__":
    main()
   

 
    
    
    
    
