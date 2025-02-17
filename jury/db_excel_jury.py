import os
import re
from datetime import datetime
import json
import glob
from difflib import SequenceMatcher
import pandas as pd



def json_to_excel(json_file, excel_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["date", "location"])  

    df.to_excel(excel_file, index=False, columns=["date", "location", "bundesland", "title", "text"])


def main():
    folder_path ="./" 
    json_to_excel('output_jury.json','jury.xlsx')

if __name__ == "__main__":
    main()
   

 
    
    
    
    
