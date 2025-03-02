import re
import json

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
    return match.group()

# Get birth year from wiki main text
main_text = PATH + PERSON2 + 'text.txt'
pattern = r"Category:\b[12]\d{3}\b births" # 4 digit number beginning with a 1 or a 2
x = get_match(main_text, pattern)

byear = int( x[9:13] )           # extract birth yeat as int
print("birth year = ", byear)

# Get photo year from INFOBOX caption
infobox = PATH + PERSON + 'infobox_captions.json'
pattern = r"\b[12]\d{3}\b"
year = int( get_match(infobox, pattern) )
print("year from infobo caption=,", year)

# 

