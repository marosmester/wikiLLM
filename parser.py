import numpy as np
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import wikipedia
import sys
sys.stdout.reconfigure(encoding='utf-8')

PATH_TO_DATABASE = "./minisubset02"
OUTPUT_FILE_NAME = "parsed_data"

def check_raster_image(image_name : str):
    """
    Helper function to check if image is a raster (assuming vector images are unlikely to be images of persons)
    Args:
        image_name (string) - name of the image in the directory
    Returns:
        bool - True if image is a raster image
    """
    supported_formats = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".ppm"]
    return any(image_name.lower().endswith(ext) for ext in supported_formats)

def file_in_directory(path : str, file : str):
    """
    Helper function to check if file is in directory
    Args:
        path_to_person (string) - relative or absolute path to the directory
        file (string) - file name
    Returns:
        bool - True if file is in the directory
    """
    return os.path.isfile(os.path.join(path, file))

def load_caption_json(path_to_person : str, caption_file : str):
    """
    Helper function, loads json (caption) file
    Args:
        path_to_person (string) - relative or absolute path to directory
        caption_file (string) - file name
    Returns:
        loaded json
    """
    with open(f"{path_to_person}/{caption_file}", encoding="utf8") as f:
        loaded = json.load(f)
    return loaded

def get_url_to_page(name : str, lang : str = "en"):
    wikipedia.set_lang(lang)
    try:
        url = wikipedia.page(name, auto_suggest=False, preload=False).url
        return url
    except:
        return 

def create_new_person_json(path_to_person : str, subdirectory : str, saved_filename : str, image_description : str, bbox_info : list[list[int]], url_to_wiki_page : str):
    """
    Helper function, returns a dictionary - informations about a specific image for updated json file
    """
    return {"path" : f"{path_to_person}/{subdirectory}/{saved_filename}",
                                 "caption" : image_description["caption"],
                                 "bbox_info" : bbox_info,
                                 "url" : url_to_wiki_page}

def load_bbox_desc_file(parse_bboxes, path, subdirectory, filename = "faces_with_bboxes.csv"):
    """
    Helper function to load csv with bounding box information
    Args:
        parse_bboxes (bool) - Execute the function if True
        path (string) - path to the directory (person directory)
        subdirectory (string) - name of the subdirectory (images/title_images)
        filename (string) - file name
    Returns:
        loaded_csv (pd.DataFrame) - loaded csv file with bbox information
    """
    if not parse_bboxes:
        return
    sub_path = f"{path}/{subdirectory}"
    if file_in_directory(sub_path, filename):
        file_path = f"{sub_path}/{filename}"
        with open(file_path, encoding="utf8") as f:
            try:
                loaded_csv = pd.read_csv(f)
            except (pd.errors.EmptyDataError, FileNotFoundError):
                loaded_csv = None

        return loaded_csv
    
def select_relevant_bboxes(parse_bboxes : bool, bbox_df : pd.DataFrame, filename : str):
    """
    Helper function to prepare the bounding box information format (list of lists of 8 integers)
    for updated json files
    Args:
        parse_bboxes (bool) - Execute if True
        bbox_df (pd.DataFrame) - loaded csv file with bounding box information
        filename (str) - file name of the picture in which the bounding boxes are
    Returns:
        None | list[list[int]] - bounding box info
    """
    if bbox_df is None or not parse_bboxes:
        return None
    relevant_bboxes = bbox_df[bbox_df['img_path'] == filename]
    relevant_bboxes_selected = relevant_bboxes.iloc[:, 1:9]
    return relevant_bboxes_selected.values.tolist()

def show_person(image_path : str, caption : str, bboxes : list[list[int]]):
    """
    Shows the image of a person with a caption (and bboxes)
    Args:
        image_path (string) - relative or absolute path to the image
        caption (string) - caption to be displayed
        bboxes (list of lists of integers | None) - if None does not show bounding boxes if it is a list of integers,
                                                    shows the bounding boxes defined by array indices as:
                                                    0 : top_left_col,
                                                    1 : top_left_row,
                                                    2 : top_right_col,
                                                    3 : top_right_row,
                                                    4 : bot_right_col,
                                                    5 : bot_right_row,
                                                    6 : bot_left_col,
                                                    7 : bot_left_row
    Returns:
        None
    """
    _, ax = plt.subplots(figsize=(6, 6))
    img = plt.imread(image_path)
    ax.imshow(img)
    ax.axis('off')
    ax.set_title(caption, fontsize=12, pad=10)
    
    if bboxes is not None:
        for bbox in bboxes:
            top_left_col, top_left_row, top_right_col, top_right_row, \
            bot_right_col, bot_right_row, bot_left_col, bot_left_row = bbox
            
            width = top_right_col - top_left_col
            height = bot_left_row - top_left_row

            rect = patches.Rectangle((top_left_col, top_left_row), width, height,
                                    linewidth=2, edgecolor='red', facecolor='none')
            ax.add_patch(rect)
    plt.show()


def mine_data_for_person(path : str,
                           person_name : str,
                           captions : list[str] = ["captions.json", "infobox_captions.json"],
                           parse_bboxes : bool = True):
    """
    Return a list of dictionaries describing images of a specific person within the database.
    Each dictionary representing one image containing:
                path to image
                image caption
                bounding box information of faces within the image
    Args:
        path (string) - path to the directory which contains all persons
        person_name (string) - name of the directory containing the information about a person
        captions (list of strings) - list of file names with caption information. !!!! CURRENTLY SUPPORTS ONLY THE DEFAULT OPTION!!!
        parse_bboxes (bool) - Load and save bounding box information if True
    Returns:
        list[dict{"path", "caption", "bbox_info"}] - list of dictionaries containing the information of specific images
    """
    path_to_person = f"{path}/{person_name}"
    updated_json = []
    for caption_file in captions:
        subdirectory = "images" if caption_file == "captions.json" else "title_images"
        if file_in_directory(path_to_person, caption_file):
            person_json = load_caption_json(path_to_person, caption_file)
        else:
            continue
        bbox_csv_file = load_bbox_desc_file(parse_bboxes, path_to_person, subdirectory)
        page_url = get_url_to_page(person_name)
        for image_description in person_json:
            saved_filename = image_description['saved_filename'].split("/")[-1]
            if not check_raster_image(saved_filename):
                continue
            bbox_info = select_relevant_bboxes(parse_bboxes, bbox_csv_file, saved_filename)
            cur_picture_new_json = create_new_person_json(path_to_person, subdirectory, saved_filename, image_description, bbox_info, page_url)
            updated_json.append(cur_picture_new_json)
    return updated_json

def parse_persons(path : str, show_persons : bool = False, write : bool = False, parse_subset_name : str = "parsed_data"):
    """
    Function which performs mine_data_for_person funtion on all persons within the database.
    Args:
        path (string) - path to the directory with all persons
        show_persons (bool) - Visualise if True
        write (bool) - creates a json file of the output if True
    Returns: 
        None
    """
    directory = os.listdir(path)
    jsons = []
    for person in directory:
        print(person)
        cur_person_json = mine_data_for_person(path, person)
        if show_persons:
            for elem in cur_person_json:
                show_person(elem["path"], elem["caption"], elem["bbox_info"])
        jsons.extend(cur_person_json)
        print(person, len(cur_person_json))
    if write:
        with open(f'{parse_subset_name}.json', 'w', encoding="utf8") as f:
            json.dump(jsons, f, indent=4)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = "./" + sys.argv[1]
    else:
        path = PATH_TO_DATABASE   #Path to the database of persons
    
    if len(sys.argv) > 2:
        parse_subset_name = sys.argv[2]
    else:
        parse_subset_name = OUTPUT_FILE_NAME # Name of the json file containing the parser's output
    
    print(os.getcwd())
    parse_persons(path, write=True, parse_subset_name=parse_subset_name)