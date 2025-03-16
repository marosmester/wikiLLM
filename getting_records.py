import os

def get_records():
    folder_path = os.path.join(os.getcwd(), 'minisubset')
    
    records = []
    
    for i in os.listdir(folder_path):
        path_to_outer_folder = os.path.join(folder_path, i)
        path_to_image_record = os.path.join(path_to_outer_folder, 'title_images')
        print(i)

get_records()
    
