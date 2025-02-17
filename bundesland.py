from bs4 import BeautifulSoup
import json

bundesland_cities = {
    "Bavaria": [],
    "Baden-Württemberg": [],
    "North Rhine-Westphalia": [],
    "Hesse":  [],
    "Saxony":  [],
    "Lower Saxony":  [],
    "Rhineland-Palatinate":  [],
    "Thuringia":  [],
    "Brandenburg":  [],
    "Saxony-Anhalt":  [],
    "Mecklenburg-Western Pomerania":  [],
    "Schleswig-Holstein":  [],
    "Saarland":  [],
    "Bremen":  [],
    "Berlin":  [],
    "Hamburg":  []
}

with open("bundesland_wiki.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

for li in soup.find_all("li"):
    text = li.get_text()
    if "(" in text and ")" in text:
        try: 
            city, bundesland = text.split(" (", 1)
            bundesland = bundesland.rstrip(")")
            if bundesland in bundesland_cities:
                bundesland_cities[bundesland].append(city)
        except Exception:
            pass

with open("bundesland_cities.json", "w", encoding="utf-8") as file:
    json.dump(bundesland_cities, file, ensure_ascii=False, indent=4)

print("Data saved to bundesland_cities.json")
