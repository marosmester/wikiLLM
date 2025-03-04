import json
import os
from pathlib import Path

# load person's folder into list
def person2list(path_to_subset, person) -> list[tuple]:
    '''
    Creates a list of 3-tuples of style (saved_filename, caption, path_to_image)
    
    Args:
        path_to_subset: Path object pointing to the directory with people's folders
        person: string, exact name of the person's folder

    Returns:
        ret: list of 3-tuples of style (saved_filename, caption, path_to_image)
    '''
    path_to_person = path_to_subset / person

    # create a list of ALL JSON files in this person's directory:
    caps = [path_to_person / "infobox_captions.json", 
            path_to_person / "captions.json"]
    jsonEntries = []
    for capFile in caps:
        if os.path.exists(capFile):
            with open(capFile, "r") as f:
                jsonEntries.append( json.load(f) )
        else:
            #print(f"{capFile} not found")
            pass
    
    # if no jsonEntry is found, return None
    if jsonEntries == [[]]:
        return None

    # create the list of 3-tuples:
    ret = []
    for entry in jsonEntries:
        if entry == []:
            continue
        else:
            entry = entry[0]
        # 1. saved_filename
        saved_filename = entry['saved_filename']
        saved_filename = Path(saved_filename).name
        # 2. caption
        caption = entry['caption']
        # 3. path to the image
        path_to_image = list( path_to_person.rglob(saved_filename) )[0] 
        ret.append((saved_filename, caption, path_to_image))
    return ret


# This example creates a list out of eevry person in a directory and prints it

if __name__ == "__main__":
    subsetPath = Path(os.getcwd()) / "minisubset"
    folders = [str(f.name) for f in subsetPath.iterdir()]
    folders.sort()

    cnt  = 0
    for person in folders:
        print(f"{cnt}. person= {person}")
        ret = person2list(subsetPath, person)
        print(ret)
        cnt += 1