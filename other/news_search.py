import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

folder_path = '13012025'
keyword = 'stürzt'

results = []

def extract_item_block(text, keyword):
    item_blocks = re.findall(r'<item\b[^>]*>.*?</item>', text, re.DOTALL)
    for block in item_blocks:
        if keyword in block:
            return block
    return None

def clean_html(raw_html):
    return re.sub(r'<[^>]+>', '', raw_html).strip()

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(('.rss', '.txt', '.xml')):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    item_block = extract_item_block(content, keyword)
                    if item_block:
                        cleaned_content = clean_html(item_block)
                        results.append([file, 1, cleaned_content])
                    else:
                        results.append([file, 0, None])
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

df = pd.DataFrame(results, columns=['File Name', 'stürzt', 'Item Content'])

output_file = f"{datetime.today().strftime('%Y-%m-%d')}_results.xlsx"
df.to_excel(output_file, index=False)

print(f"Results saved to {output_file}")
