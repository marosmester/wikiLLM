import re
import json
import os
from pathlib import Path
import numpy as np

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

def find_year_json_entry(jsonEntry) -> np.array:
    '''
    Search a caption in a single JSON entry for a year.
    Try multiple patterns. 

    Args:
        jsonEntry: Python dictionary created from a JSON object

    Returns:
        year: 1- or 2-element np.array of ints, depending on the accuracy of the year info. 
              2-element array indicates year interval.
    '''
    cap = jsonEntry['caption']
    no_cap = True if cap is None else False
    found = False

    # 4-digit number:
    if not found and not no_cap: 
        p = r"\b[12]\d{3}\b"    # pattern
        match = re.search(p, cap)
        if match != None:
            found = True
            year = np.array( int(match.group()) )

    # 4-digit number followed by s (e.g. 1970s or 1970's)
    if not found and not no_cap:
        p = r"\b[12]\d{3}['’]?s\b"
        match = re.search(p, cap)
        if match != None:
            found = True
            year = int( match.group()[:4] )
            year = np.array( [year, year + 9] )

    if not found:
        return None
    else:
        return year

def analyze_person(path_to_person, file = None):
    '''
    Search a person's directory and prints (writes) all years it can find.
    The years are written to a file specified in file arg. If none provided, the output
    will be printed in the  terminal
    '''
    # Get birth year from wiki main text
    main_text = path_to_person / "text.txt"
    pattern = r"Category:\b[12]\d{3}\b births" # 4 digit number beginning with a 1 or a 2
    x = find_year_file(main_text, pattern)
    if x is not None:
        byear = int( x.group()[9:13] )           # extract birth yeat as int
        print("birth year = ", byear, file= file)
    else:
        print("No birth year found in \"text.txt\".", file= file)

    # Get photo year from INFOBOX caption
    infobox = path_to_person / 'infobox_captions.json'
    if os.path.exists(infobox):
        with open(infobox, "r") as f:
            jsonData = json.load(f)
        if jsonData == []:
            print("File \"infobox_captions.json\" is empty", file=file)
        for entry in jsonData:
            year = find_year_json_entry(entry)
            print("year from infobox caption= ", year, file= file)
    else:
        print("No file named \"infobox_captions.json\" found.", file=file)
        
    # For every other non-infobox caption, calculate the age
    captions = path_to_person / "captions.json"
    if os.path.exists(captions):
        with open(captions, "r") as f:
            jsonData = json.load(f)
        if jsonData == []:
            print("File \"captions.json\" is empty", file=file)
        for entry in jsonData:
            year = find_year_json_entry(entry)
            print(f"caption= {entry["caption"]}", file = file)
            print(f"year from caption = {year}", file = file)
    else:
        print("No file named \"captions.json\" found.", file=file)

    print("-----------------------------------", file=file)
    return path_to_person

if __name__ == "__main__":
    # find all eleigible folders
    subsetPath = Path(os.getcwd()) / "minisubset"
    folders = [str(f.name) for f in subsetPath.iterdir()]
    folders.sort()

    # reset output file
    fname = "regex/output.txt"
    f = open(fname, "w")
    f.close()

    # fill out output file 
    cnt = 0
    with open(fname, "a") as file:
        for f in folders:
            print(f"{cnt} Analyzing: {f}")
            print(str(cnt) + ' ' + str(f), file= file)
            ret = analyze_person(subsetPath / f, file=file)
            cnt += 1

