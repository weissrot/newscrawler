import os
import csv
import subprocess
import time
import ast
import spacy
count = 0
input_param = f"../html/{count}/*.html"
output_param = f"./plaintext/{count}/"
os.system(f"python3 preprocessor.py -i {input_param} -o {output_param}")