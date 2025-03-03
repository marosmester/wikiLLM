import re
import json
import os

PATH = "minisubset/"
PERSON = "Alex_Webster/"
PERSON2 = "Emmy_Rossum/"
PERSON3 = "Barbara_Contini/"

def get_match(filepath, pattern):
    '''
    Search any elligible file AS IT WAS A TXT FILE.
    '''
    with open(filepath, "r") as f:
        content = f.read()
    match = re.search(pattern, content)
    print("match=", match)
    return match.group()

def find_years(person, file = None):
    '''
    Search a person's directory and prints (writes) all years it can find.
    '''
    # Get birth year from wiki main text
    main_text = PATH + person + '/text.txt'
    pattern = r"Category:\b[12]\d{3}\b births" # 4 digit number beginning with a 1 or a 2
    print("path=", main_text)
    x = get_match(main_text, pattern)
    byear = int( x[9:13] )           # extract birth yeat as int
    print("birth year = ", byear, file= file)

    # Get photo year from INFOBOX caption
    infobox = PATH + person + '/infobox_captions.json'
    if os.path.exists(infobox):
        pattern = r"\b[12]\d{3}\b"
        year = int( get_match(infobox, pattern) )
        print("year from infobox caption=,", year, file= file)
    else:
        print("No file named \"infobox_captions.json\" found.", file=file)
        
    # For every other non-infobox caption, calculate the age
    captions = PATH + person + "/captions.json"
    if os.path.exists(captions):
        with open(captions, "r") as f:
            data = json.load(f)

        pattern = r"\b[12]\d{3}\b"
        for entry in data:
            caption = entry["caption"]
            match = re.search(pattern, caption)
            year = int( match.group() )
            print(f"caption= {caption}", file = file)
            print(f"year from caption = {year}", file = file)
    else:
        print("No file named \"captions.json\" found.", file=file)

    print("-----------------------------------", file=file)
    return person

if __name__ == "__main__":
    # find all eleigible folders
    folders = [str(f) for f in os.listdir("minisubset/")]
    folders.sort()  # alphabetically

    # reset output file
    fname = "regex/output.txt"
    f = open(fname, "w")
    f.close()

    # fill out output file 
    cnt = 0
    with open(fname, "a") as file:
        print(cnt, file= file)
        for f in folders:
            ret = find_years(f, file=file)
            print(ret)
