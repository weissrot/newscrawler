import pandas as pd
import json
import glob 

with open("bundesland_cities.json", "r", encoding="utf-8") as file:
    bundesland_cities = json.load(file)

def find_city_in_text(text):  
    words = text.replace(',','').replace('.','').lower().split()  
    for bundesland, cities in bundesland_cities.items():  
        for city in cities:  
            if city.lower() in words:  
                return bundesland, city  
    return None, None  

matches = []
for file in glob.glob("scraped_news/*.txt"):  
    print(file)
    file_name = file.rsplit("\\", 1)[-1]
    print(file_name)
    try: 
        content = open(file).read()
    except Exception:
        pass
  #to change: do not check each line, check each text as a whole
    if content: 
        for line in content.splitlines():
            if len(line)>5:
                bundesland, city = find_city_in_text(line)
                if city:
                    matches.append({"City": city, "Bundesland": bundesland, "Text": line})
                    break

df = pd.DataFrame(matches)
df.to_excel(f"output1/{file_name}.xlsx", index=False)
