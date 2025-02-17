import os
import json
from bs4 import BeautifulSoup
import glob
import re

output_file = "output_jury.json"

data = []  # List to store extracted data
def find_city_in_text(text):  
    words = text.replace(',','').replace('.','').replace('(','').replace(')','').replace("'",'').replace('"','').lower().split()  
    for bundesland, cities in bundesland_cities.items():  
        for city in cities:  
            if city.lower() in words:  
                return bundesland, city  
    return None, None  

          
with open("../bundesland_cities.json", "r", encoding="utf-8") as file:
    bundesland_cities = json.load(file)

def extract_info(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    description_meta = soup.find("meta", {"name": "description"})
    title = description_meta["content"] if description_meta else "Unknown Title"
    keywords_meta = soup.find("meta", {"name": "keywords"})
    keywords_content = keywords_meta["content"] if keywords_meta else ""
    date = re.search(r"\d{2}\.\d{2}\.\d{4}", keywords_content).group() if re.search(r"\d{2}\.\d{2}\.\d{4}", keywords_content) else "Unknown Date"

    if keywords_content:
        location = re.search(r"olg (\w+),", keywords_content, re.IGNORECASE).group(1) if re.search(r"olg (\w+),", keywords_content, re.IGNORECASE) else "Unknown Location"
        bundesland,_=find_city_in_text(location)

    paragraphs = soup.find_all("p")
    text_content = "\n".join(p.get_text(strip=True) for p in paragraphs) if paragraphs else "No text found"

    return {"title": title, "date": date,"bundesland":bundesland, "location": location, "text": text_content}

html_files = glob.glob("../html/*/*.html", recursive=True)
# for filename in os.listdir(html_folder):
#     if filename.endswith(".html"):
for file_path in html_files:
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()
        extracted_data = extract_info(html_content)
        data.append(extracted_data)

with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, indent=4, ensure_ascii=False)

print(f"Extraction complete! Data saved in {output_file}")
