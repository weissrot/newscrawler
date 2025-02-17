import re  
import pandas as pd
import json
import glob 

def date_extraction(text):
    date = None
    months = {"Januar": "01", "Februar": "02", "März": "03", "April": "04", "Mai": "05", "Juni": "06", "Juli": "07", "August": "08", "September": "09", "Oktober": "10", "November": "11", "Dezember": "12"}  
    date_match = re.search(r'(\d{1,2})\.\s*(\w+)|(\w+)\.\s*(\d{1,2})', text)  
    date_match1 = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', text)   
    try:
        if date_match: date = f"2025-{months[date_match.group(2) if date_match.group(2) else date_match.group(3)]}-{date_match.group(1) if date_match.group(1) else date_match.group(4)}"  
    except Exception:
        pass
    if date_match1: date = f"{date_match1.group(3)}-{date_match1.group(2)}-{date_match1.group(1)}"   
    return date


matches = []
date = None
for file in glob.glob("scraped_news/*.txt")[9:10]:  
    file_name = file.rsplit("\\", 1)[-1]
    print(file_name)
    content = None
    try: 
        content = open(file).read()
    except Exception:
        pass
  #to change: do not check each line, check each text as a whole
    if content: 
        for line in content.splitlines():
            print(line)
            date = date_extraction(line)
            if date:
                print(file_name)
                print(date)
                break
 