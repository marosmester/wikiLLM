import re
import json
import os
from pathlib import Path
import numpy as np

def write_to_json(self) -> None:        
    person_data = self.data_from_annotation[self.person_index]  # one person can include multiple images
    pathstring = (person_data[0]["path"].rsplit("/",2))[0]      # get only the path to the person folder
    path_to_annotation = Path(pathstring) / "annotation.json"

    jsonData = []
    for img in person_data:
        jsonData.append(img)

    with open(path_to_annotation , "w") as f:
        json.dump(jsonData, f, indent=4)

def find_birth_year(path_to_person):
    '''
    Finds the person's birth year in the wikipedia body text file.  
    '''
    # Get birth year from wiki main text
    main_text = path_to_person / "text.txt"
    pattern = r"Category:\b[12]\d{3}\b births" # 4 digit number beginning with a 1 or a 2
    x = find_year_file(main_text, pattern)
    if x is not None:
        byear = int( x.group()[9:13] )           # extract birth yeat as int
    else:
        byear = None

    return byear

def find_year_file(fpath, pattern):
    '''
    Search any elligible file AS IT WAS A TXT FILE.
    '''
    #print(fpath)
    with open(fpath, "r") as f:
        content = f.read()
    match = re.search(pattern, content)
    return match

