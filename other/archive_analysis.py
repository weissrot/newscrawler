import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

folder_path = 'archive'
keyword = 'stürzt'
rss_list_file = 'rss_source.txt'
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

os.makedirs(folder_path, exist_ok=True)
results = []

def download_rss_feed(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        first_word = url.split('/')[2].split('.')[0]
        file_name = f"{timestamp}_{first_word}.xml"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Downloaded: {file_name}")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def extract_item_block(text, keyword):
    item_blocks = re.findall(r'<item\b[^>]*>.*?</item>', text, re.DOTALL)
    for block in item_blocks:
        if keyword in block:
            return block
    return None

def clean_html(raw_html):
    return re.sub(r'<[^>]+>', '', raw_html).strip()

with open(rss_list_file, 'r') as file:
    rss_links = file.read().splitlines()

for rss_link in rss_links:
    file_path = download_rss_feed(rss_link)
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                item_block = extract_item_block(content, keyword)
                if item_block:
                    cleaned_content = clean_html(item_block)
                    results.append([file_path, 1, cleaned_content])
                else:
                    results.append([file_path, 0, None])
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

output_file = f"{timestamp}_archive_analyse.xlsx"
df = pd.DataFrame(results, columns=['File Name', 'stürzt', 'Item Content'])
df.to_excel(output_file, index=False)

print(f"Results saved to {output_file}")
