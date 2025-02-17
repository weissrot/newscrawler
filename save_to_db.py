import psycopg2
import json


tasks = ["arbeit","haushalt","freizeit"]

def remove_duplicates(json_data):
    seen = set()
    unique_data = []
    for item in json_data:
        identifier = (item['Date'], item['City'])  # Tuple of Date and City
        if identifier not in seen:
            unique_data.append(item)
            seen.add(identifier)
    return unique_data


def main(): 
    conn = psycopg2.connect(
        host="10.10.144.85", database="up_testdb", user="up_testdb", password="Ggs!87NBsfdlkw", port=5432
    )
    cursor = conn.cursor()
    for task in tasks:      
        with open(f'{task}/output.json', 'r', encoding="UTF-8") as file:
            data = json.load(file)
            data = remove_duplicates(data)
            for item in data:
                title = f"{task} unfall: " + item['File'].replace('.txt','') 
                date = item['Date']
                if date and int(date.split('-')[0]) > 2024:
                    cursor.execute("INSERT INTO ergo.events_selenium (article_date, article_location, article_state, article_title, article_text) VALUES (%s, %s, %s, %s, %s)", 
                                (item['Date'], item['City'], item['Bundesland'], title, item['Text']))

    clear_redundant_script = """
DELETE FROM dein_tabellenname
WHERE id NOT IN (SELECT MIN(id) FROM dein_tabellenname GROUP BY location, date);
""" 
    cursor.execute(clear_redundant_script)
    conn.commit()
    cursor.close()
    conn.close()
    
if __name__ == "__main__":
    main()
