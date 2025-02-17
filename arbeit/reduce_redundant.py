from difflib import SequenceMatcher
import json  

with open("output.json",encoding="utf-8") as f: items = json.load(f) 

def filter_similar_items(items):
    unique_items = []
    seen = {}

    for item in items:
        key = (item["City"], item["Date"])
        first_30 = " ".join(item["Text"].split()[:30])
        if key in seen and SequenceMatcher(None, seen[key], first_30).ratio() > 0.5:
            continue
        seen[key] = first_30
        unique_items.append(item)

    return unique_items

filtered_items = filter_similar_items(items)  
with open("filtered_data.json", "w", encoding="utf-8") as f: json.dump(filtered_items, f)  
