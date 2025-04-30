import webbrowser
import tkinter as tk
import ttkbootstrap as tb
from PIL import Image, ImageTk
from ttkbootstrap.scrolled import ScrolledText
from tkinter.scrolledtext import ScrolledText 
import numpy as np
import cv2
import datetime
import webview
import multiprocessing
import json
import platform
from pathlib import Path
#from regex.helper_functions import find_birth_year
import parser as psr
import time
import sys
import re

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
    with open(fpath, "r", encoding='utf-8') as f:
        content = f.read()
    match = re.search(pattern, content)
    return match
 
def multiProcessWeb(link):
    """
    Creates and displays a webview window for the given link.
    This function initializes a webview window with the specified link, 
    sets its dimensions and position, and starts the webview using the GTK GUI framework.
    Args:
        link (str): The URL to be displayed in the webview window.
    Notes:
        - The window is titled "Wikipedia" and is set to always stay on top.
        - The position of the window is slightly offset with x=-10 and y=-2.
        - The dimensions of the window are 650 pixels wide and 840 pixels high.
        - Requires the `webview` library to be installed and GTK to be available.
    """
    
    web = webview.create_window("Wikipedia", link, on_top=True, x=-10, y=-2, width=650, height=840)
    webview.start(gui='gtk')
    
def imread_unicode(path, flags=cv2.IMREAD_COLOR):
    """
    Reads an image from a file path that may contain Unicode characters.
    This function handles file paths with Unicode characters by reading the file
    as a numpy array of bytes and then decoding it into an image using OpenCV.
    Args:
        path (str): The file path to the image. Can include Unicode characters.
        flags (int, optional): Flags specifying the color type of the loaded image.
            Defaults to cv2.IMREAD_COLOR.
    Returns:
        numpy.ndarray: The decoded image as a NumPy array. Returns None if the image
        cannot be decoded.
    """
    
    # Read the file as a numpy array of bytes
    data = np.fromfile(path, dtype=np.uint8)
    # Decode the image from the byte array
    return cv2.imdecode(data, flags)


class AnnotationTool(tb.Window):
    def __init__(self, parsed_data_json, title="Annotation Tool", themename="litera", iconphoto='', size=None, position=None, minsize=None, maxsize=None, resizable=None, hdpi=True, scaling=None, transient=None, overrideredirect=False, alpha=1, web_mode="pywebview"):
        """
        Initializes the Annotation Tool application with various configurations, widgets, and attributes.
        Parameters:
            title (str): The title of the application window. Defaults to "Annotation Tool".
            themename (str): The theme name for the application. Defaults to "litera".
            iconphoto (str): The file path to the icon image for the application. Defaults to an empty string.
            size (tuple): The size of the application window (width, height). Defaults to None.
            position (tuple): The position of the application window (x, y). Defaults to None.
            minsize (tuple): The minimum size of the application window (width, height). Defaults to None.
            maxsize (tuple): The maximum size of the application window (width, height). Defaults to None.
            resizable (tuple): A tuple indicating whether the window is resizable (width, height). Defaults to None.
            hdpi (bool): Whether to enable high DPI scaling. Defaults to True.
            scaling (float): The scaling factor for the application. Defaults to None.
            transient (bool): Whether the window is transient. Defaults to None.
            overrideredirect (bool): Whether to override the window manager decorations. Defaults to False.
            alpha (float): The transparency level of the window (0.0 to 1.0). Defaults to 1.
        Attributes:
            caption_font (tuple): Font settings for captions.
            info_font (tuple): Font settings for informational text.
            frames (dict): Dictionary to store frame widgets.
            buttons (dict): Dictionary to store button widgets.
            labels (dict): Dictionary to store label widgets.
            entries (dict): Dictionary to store entry widgets.
            texts (dict): Dictionary to store text widgets.
            comboboxes (dict): Dictionary to store combobox widgets.
            menus (dict): Dictionary to store menu widgets.
            checkbuttons (dict): Dictionary to store checkbutton widgets.
            IMAGE_NEXT (ImageTk.PhotoImage): Image for the "Next" button.
            IMAGE_PREVIOUS (ImageTk.PhotoImage): Image for the "Previous" button.
            image (Any): Placeholder for the current image.
            caption (Any): Placeholder for the current caption.
            name (Any): Placeholder for the person's name.
            birth_day (Any): Placeholder for the person's birth day.
            birth_month (Any): Placeholder for the person's birth month.
            birth_year (Any): Placeholder for the person's birth year.
            link (Any): Placeholder for the Wikipedia link.
            scaling_factor (Any): Placeholder for the scaling factor.
            bounding_box_index (Any): Placeholder for the bounding box index.
            person_index (int): Index of the current person. Defaults to 0.
            person_sub_index (int): Sub-index of the current person. Defaults to 0.
            web_proc (Any): Placeholder for the web process.
            data_from_annotation (Any): Placeholder for annotation data.
            possible_to_annotate_birth (tk.IntVar): Variable to track if birth annotation is possible.
            possible_to_annotate_creation (tk.IntVar): Variable to track if image creation annotation is possible.
            possible_to_annotate_face (tk.IntVar): Variable to track if bounding box annotation is possible.
            data (dict): Loaded data from the JSON database.
        Methods:
            nextRecord: Navigates to the next record.
            previousRecord: Navigates to the previous record.
            possToFullyAnnotateCallback: Callback for handling incomplete annotations.
            catRelatedImages: Categorizes related images.
            defaultScreenBuild: Builds the default screen layout.
        """
        super().__init__(title, themename, iconphoto, size, position, minsize, maxsize, resizable, hdpi, scaling, transient, overrideredirect, alpha)
        self.parsed_data_json = parsed_data_json

        # Set the window size - platform specific workaround
        if platform.system() == "Windows":
            self.state("zoomed")  # works on Windows
        elif platform.system() == "Linux":
            self.wm_attributes("-zoomed", True)  # works on Ubuntu
        #--------------------------------------------------------------------------------------------

        # Set font styles
        self.caption_font = ("Helvetica", 30, "bold")
        self.info_font = ("Helvetica", 16)
        #--------------------------------------------------------------------------------------------
        
        # Widget dictionaries initialization
        self.frames = {'Person_info_frame': {},
                       'Image_creation_frame_plus_pixel_pos': {}}
        self.buttons = {'Person_info_frame': {}}
        self.labels = {'Person_info_frame': {},
                       'Image_creation_frame_plus_pixel_pos': {},
                       'Control_panel': {}}
        self.entries = {'Person_info_frame': {},
                        'Control_panel': {}}
        self.texts = {'Person_info_frame': {}}
        self.comboboxes = {'Person_info_frame': { "Birth":  {}},
                           'Image_creation_frame_plus_pixel_pos': {}}
        self.menus = {}
        self.checkbuttons = {}
        #--------------------------------------------------------------------------------------------
        
        # Class attributes initialization
        self.IMAGE_NEXT = ImageTk.PhotoImage(file = 'graphics/nextRecord.png')
        self.IMAGE_PREVIOUS = ImageTk.PhotoImage(file='graphics/previousRecord.png')
        self.IMAGE_SAVE = ImageTk.PhotoImage(file='graphics/diskette.png')
        self.IMAGE_SKIP = ImageTk.PhotoImage(file='graphics/fast-forward.png')
        self.image = None
        self.caption = None
        self.name = None
        self.birth_day = None
        self.birth_month = None
        self.birth_year = None
        self.link = None
        self.scaling_factor = None
        self.bounding_box_index = None
        self.person_index = 0
        self.person_sub_index = 0
        self.web_proc = None
        self.data_from_annotation = None
        self.possible_to_annotate_birth = tk.IntVar(value=1)
        self.possible_to_annotate_creation = tk.IntVar(value=1)
        self.possible_to_annotate_face = tk.IntVar(value=1)
        self.possible_to_annotate_sufficient = tk.IntVar(value=1)
        self.person_pixel_position = None
        self.theme = themename
        self.web_mode = web_mode
        #--------------------------------------------------------------------------------------------
        
        # Create a frame
        
        #Left half of the screen
        self.frames["Image"] = tb.Frame(self, padding=10)
        self.frames["Caption"] = tb.Labelframe(self, text="Image caption", padding=10)
        
        #Right half of the screen
        
        #Main frames
        self.frames["Name"] = tb.Frame(self, padding=10)
        self.frames["Database_info"] = tb.Labelframe(self, text="Database info", padding=10)
        self.frames["Person_info_frame"]["MAIN"] = tb.Labelframe(self, text = 'Annotation essentials' ,padding=10)
        self.frames["Annotation_fail"] = tb.Labelframe(self, text="Annotation shortcomings", padding=10)
        self.frames["First_paragraph"] = tb.Labelframe(self, text="First wikipedia paragraph", padding=10)
        self.frames["Control_panel"] = tb.Labelframe(self, padding=10, text="Control panel")
        
        #Subframes
        self.frames["Annotation_status"] = tb.Labelframe(self.frames["Database_info"], padding=10, text="Annotation status")
        self.frames["Person_id"] = tb.Labelframe(self.frames["Database_info"], text="Person ID", padding=10)
        self.frames["Annotation_percentage"] = tb.Labelframe(self.frames["Database_info"], text="Annotated", padding=10)
        self.frames["Wiki_page_sufficient_for_annotation"] = tb.Frame(self.frames["Person_info_frame"]["MAIN"], padding=10)
        self.frames["Person_info_frame"]["Birth"] = tb.Labelframe(self.frames["Person_info_frame"]["MAIN"], text="Birth Date", padding=10)
        self.frames["Person_info_frame"]["Wiki_link"] = tb.Labelframe(self.frames["Person_info_frame"]["MAIN"], text="Link to Wikipedia website", padding=10)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"] = tb.Labelframe(self.frames["Person_info_frame"]["MAIN"], text="Estimated year interval of image creation", padding=10)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"] = tb.Labelframe(self.frames["Person_info_frame"]["MAIN"], text="Pixel position of the person", padding=10)
        #---------------------------------------------------------------------------------------------
        
        # Create a label
        
        #Image
        self.labels["Image"] = tb.Label(self.frames["Image"])
        
        #Caption
        self.labels["Caption"] = tb.Label(self.frames["Caption"], font=self.caption_font)
        
        #Person name
        self.labels["Person_info_frame"]["Name"] = tb.Label(self.frames["Name"], font=self.caption_font)
        
        #Status frame
        self.labels["Annotation_status"] = tb.Label(self.frames["Annotation_status"], text="Unannotated", font=self.info_font)
        self.labels["Person_id"] = tb.Label(self.frames["Person_id"], text="Person ID", font=self.info_font)
        self.labels["Annotation_percentage"] = tb.Label(self.frames["Annotation_percentage"], text="Annotated", font=self.info_font)
        
        #Wiki link
        self.labels["Wiki_link"] = tb.Label(self.frames["Person_info_frame"]["Wiki_link"], text="Link to Wikipedia page", foreground="#2780e3", cursor="hand2", font=self.info_font)
        
        #Image creation frame
        self.labels["Image_creation_frame_plus_pixel_pos"][";"] = tb.Label(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], text=";", font=self.info_font)
        self.labels["Image_creation_frame_plus_pixel_pos"]["("] = tb.Label(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], text="(", font=self.info_font)
        self.labels["Image_creation_frame_plus_pixel_pos"][")"] = tb.Label(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], text=")", font=self.info_font)
        
        #Pixel position frame
        self.labels["Image_creation_frame_plus_pixel_pos"]["px"] = tb.Label(self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"], text="Click on the image", font=self.info_font, width=15)
        
        # Person info frame
        self.labels["Wiki_page_sufficient_for_annotation"] = tb.Label(self.frames["Wiki_page_sufficient_for_annotation"], text="Wikipedia page sufficient for annotation?", font=self.info_font)
        
        #Control panel
        self.labels["Control_panel"]["/"] = tb.Label(self.frames["Control_panel"], font=self.info_font)
        #---------------------------------------------------------------------------------------------
        
        # Create a text widget
        
        #Caption
        self.texts["Caption"] = ScrolledText(self.frames["Caption"], font=self.info_font, height = 2, width=30, wrap= "word")
        
        #Annotation shortcomings
        self.texts["Pos_to_annote"] = tb.ScrolledText(self.frames["Annotation_fail"], font=self.info_font, height=1, width=30, wrap="word")
        
        #First paragraph
        self.texts["First_paragraph"] = tb.ScrolledText(self.frames["First_paragraph"], font=self.info_font, height=1, width=30, wrap="word")
        #---------------------------------------------------------------------------------------------
        
        # Create an entry widget
                
        #Control panel
        self.entries["Control_panel"]["LEFT"] = tb.Entry(self.frames["Control_panel"], font=self.info_font, width=2, justify="center")
        self.entries["Control_panel"]["RIGHT"] = tb.Entry(self.frames["Control_panel"], font=self.info_font, width=2, justify="center")
        #---------------------------------------------------------------------------------------------
        
        #Create a combo box widget
        
        #Person birth frame
        self.comboboxes["Person_info_frame"]["Birth"]["Day"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values=[str(i) for i in range(1,32)], width=2, justify="right")
        self.comboboxes["Person_info_frame"]["Birth"]["Month"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], width=10, justify="right")
        self.comboboxes["Person_info_frame"]["Birth"]["Year"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4, justify="right")
        
        #Image creation frame
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"] = tb.Combobox(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4, justify="right")
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"] = tb.Combobox(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4, justify="right")
        #---------------------------------------------------------------------------------------------
        
        #Create a button widget
        
        #Control panel buttons
        self.buttons["Next"] = tb.Button(self.frames["Control_panel"], image = self.IMAGE_NEXT, command = self.nextRecordWithoutSaving , padding=10, width=100, takefocus=False)
        self.buttons["Previous"] = tb.Button(self.frames["Control_panel"], image = self.IMAGE_PREVIOUS, command= self.previousRecord, padding=10, width=10, takefocus=False)
        self.buttons["Save"] = tb.Button(self.frames["Control_panel"], image=self.IMAGE_SAVE, command=self.saveAnnotation, padding=10, width=10, takefocus=False)
        self.buttons["Skip_to_the_first_unannotated"] = tb.Button(self.frames["Control_panel"], image = self.IMAGE_SKIP, command=self.skipToFirstUnannotated, padding=10, width=10, takefocus=False)
        #---------------------------------------------------------------------------------------------
        
        #Create a checkbutton widget
        
        #Person birth frame
        self.checkbuttons["Birth"] = tb.Checkbutton(self.frames["Person_info_frame"]["Birth"], width=3, bootstyle = "round-toggle", command=self.possToFullyAnnotateCallback, variable=self.possible_to_annotate_birth)

        #Image creation frame
        self.checkbuttons["Creation"] = tb.Checkbutton(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], width=3, bootstyle="round-toggle", command=self.possToFullyAnnotateCallback, variable=self.possible_to_annotate_creation)
        
        #Pixel position frame
        self.checkbuttons["Face"] = tb.Checkbutton(self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"], width=3, bootstyle="round-toggle", command=self.possToFullyAnnotateFace, variable=self.possible_to_annotate_face)
        
        #Person info frame
        self.checkbuttons["Wiki_page_sufficient_for_annotation"] = tb.Checkbutton(self.frames["Wiki_page_sufficient_for_annotation"], width=3, bootstyle="round-toggle", command=self.possToFullyAnnotateCallback, variable=self.possible_to_annotate_sufficient)
        
        #---------------------------------------------------------------------------------------------
        
        #Load database
        with open(self.parsed_data_json, "r") as file:
            self.data = json.load(file)

        #Reorder the data
        self.catRelatedImages()

        #Fill already annotated images into self.data_from_annotation
        self.loadAlreadyAnnotated()

        #---------------------------------------------------------------------------------------------
        
        #Build the default screen layout
        self.defaultScreenBuild()

        #Skip to the 1st unannotated image
        self.skipToFirstUnannotated()

        self.setAnnotationStatus()

    
    def possToFullyAnnotateCallback(self) -> None:
        """
        Callback function to handle the state of the "Pos_to_annote" text widget 
        based on the selection state of checkbuttons.
        This function iterates through all checkbuttons in the `self.checkbuttons` 
        dictionary. If any checkbutton is not in the "selected" state, it enables 
        the "Pos_to_annote" text widget for editing. Otherwise, it clears the 
        content of the "Pos_to_annote" text widget and disables it.
        Returns:
            None
        """
        
        Disabled = False
        for _, button in self.checkbuttons.items():
            if button.instate(["selected"]) == False:
                Disabled = True
                break

        if(Disabled):
            self.texts["Pos_to_annote"].config(state="normal")
        else:
            self.texts["Pos_to_annote"].delete("1.0", tk.END)
            self.texts["Pos_to_annote"].config(state="disabled")
            
    def possToFullyAnnotateFace(self) -> None:
        if self.checkbuttons["Face"].instate(["selected"]) == False:
            self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="No correct bounding box!")
            self.bounding_box_index = None
        else:
            self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="Click on the image")
        
        self.readImage()    
        self.possToFullyAnnotateCallback()
    
    def catRelatedImages(self) -> None:
        """
        Groups related images in the dataset based on the person identifier in their file paths.
        This method processes the `self.data` list, which contains dictionaries with image metadata,
        and organizes the images into groups where each group corresponds to a unique person identifier
        extracted from the file path. The grouped data is then reassigned to `self.data`.
        The file path is expected to have the format where the person identifier is the third element
        when split by the "/" character.
        Returns:
            None
        """
        
        last_person = None
        new_data = []
        index = -1
        
        for i in range(len(self.data)):
            parsed_path = self.data[i]["path"].split("/")
            
            if parsed_path[2] == last_person:
                new_data[index].append(self.data[i])
            else:
                new_data.append([self.data[i]])
                index += 1
                
            last_person = parsed_path[2]
        
        self.data = new_data
                    
    def readCaption(self) -> None:
        """
        Reads the caption for the current person and sub-index from the data structure
        and updates the corresponding text widget in the GUI.
        If the caption is `None`, it sets the caption to an empty string. Otherwise,
        it retrieves the caption from the data structure. The method then updates
        the "Caption" text widget by enabling it, clearing its current content,
        inserting the new caption, and disabling it again to make it read-only.
        Attributes:
            self.data (list): A nested list or similar data structure containing
                information about persons and their captions.
            self.person_index (int): The index of the current person in the data structure.
            self.person_sub_index (int): The sub-index of the current person in the data structure.
            self.caption (str): The caption text retrieved from the data structure.
            self.texts (dict): A dictionary of text widgets, where "Caption" is the key
                for the caption text widget.
        """
        
        if self.data[self.person_index][self.person_sub_index]["caption"] == None:
            self.caption = ""
        else:
            # filter out wikipedia position tags (they are separated by "|" symbol)
            self.caption = self.data[self.person_index][self.person_sub_index]["caption"]
            bracket_pairs = self.createBracketPairs()
            bar_indices = [i for i, c in enumerate(self.caption) if c == "|"]
            bar_indices = bar_indices[::-1]
            pos_outside_brackets = None
            for ind in bar_indices:
                inside = False
                for pair in bracket_pairs:
                    if ind > pair[0] and ind < pair[1]:     # "|" is inside []
                        inside = True
                        break
                if inside:
                    continue
                else:
                    pos_outside_brackets = ind
                    break

            if pos_outside_brackets != None and (pos_outside_brackets+1) < len(self.caption):
                self.caption = self.caption[pos_outside_brackets+1:]

        self.texts["Caption"].config(state="normal")
        self.texts["Caption"].delete("1.0", "end")
        self.texts["Caption"].insert("1.0", self.caption)
        self.texts["Caption"].config(state="disabled")
    
    def createBracketPairs(self):
        """
        Parses the caption and returns all [] bracket pair indeces as 2-tuples in a list
        """
        lBuffer = []
        ret = []
        cnt = 0
        for char in self.caption:
            if char == "[":
                lBuffer.append(cnt)
            elif char == "]" and len(lBuffer) != 0:
                leftInd = lBuffer.pop()
                ret.append( (leftInd, cnt) )
            cnt += 1

        return ret  

    def readImage(self) -> None:
        """
        Reads and processes an image, resizes it to fit within the specified frame, 
        draws bounding boxes on the image, and updates the Tkinter label with the processed image.
        Steps:
        1. Updates the frame size for displaying the image.
        2. Reads the image from the specified file path.
        3. Resizes the image to fit within the frame while maintaining the aspect ratio.
        4. Draws bounding boxes on the resized image based on the provided bounding box information.
        5. Highlights a specific bounding box if `bounding_box_index` is set.
        6. Converts the image from BGR to RGB format.
        7. Converts the processed image to a PIL Image and then to a Tkinter PhotoImage.
        8. Updates the Tkinter label to display the processed image.
        Attributes:
            self.image_frame_size (tuple): The width and height of the frame for displaying the image.
            self.scaling_factor (float): The factor by which the image is resized.
            self.image (ImageTk.PhotoImage): The processed image to be displayed in the Tkinter label.
        Raises:
            FileNotFoundError: If the image file specified in the path does not exist.
            ValueError: If the bounding box information is invalid or improperly formatted.
        """
        
        # step 1: Read the requested image size
        self.update()
        self.image_frame_size = (self.frames["Image"].winfo_width(), self.frames["Image"].winfo_height())
        
        # Step 2: Read the image
        img = imread_unicode(self.data[self.person_index][self.person_sub_index]["path"])
        h, w = img.shape[:2]
        
        resizing_factor = min(self.image_frame_size[0]/w, self.image_frame_size[1]/h)
        self.scaling_factor = resizing_factor
        resized_img = cv2.resize(img, (int(w*resizing_factor), int(h*resizing_factor)), interpolation=cv2.INTER_AREA)
        
        # Draw the bounding boxes
        if self.data[self.person_index][self.person_sub_index]["bbox_info"] != None:
            for i in range(len(self.data[self.person_index][self.person_sub_index]["bbox_info"])):
                bbox = self.data[self.person_index][self.person_sub_index]["bbox_info"][i]
                #cv2.rectangle(resized_img, (int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)),
                #              (int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)), (0, 255, 0), 3)
                cv2.polylines(resized_img, [np.array([[int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)],
                                                    [int(bbox[2]*self.scaling_factor), int(bbox[3]*self.scaling_factor)],
                                                    [int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)],
                                                    [int(bbox[6]*self.scaling_factor), int(bbox[7]*self.scaling_factor)]],np.int32)], color=(0, 255, 0), isClosed=True, thickness=3)
                                                 

        if self.checkbuttons["Face"].instate(["selected"]):
            if self.bounding_box_index != None or len(self.data[self.person_index][self.person_sub_index]["bbox_info"]) == 1:
                if self.bounding_box_index != None:
                    bbox = self.data[self.person_index][self.person_sub_index]["bbox_info"][self.bounding_box_index]
                else:
                    bbox = self.data[self.person_index][self.person_sub_index]["bbox_info"][0]
                    self.bounding_box_index = 0
                    
                overlay = resized_img.copy()
                #cv2.rectangle(overlay, (int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)),
                #              (int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)), (0, 255, 0), thickness=-1)
                cv2.fillPoly(resized_img, [np.array([[int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)],
                                                    [int(bbox[2]*self.scaling_factor), int(bbox[3]*self.scaling_factor)],
                                                    [int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)],
                                                    [int(bbox[6]*self.scaling_factor), int(bbox[7]*self.scaling_factor)]],np.int32)], color=(0, 255, 0))
                
                cv2.addWeighted(overlay, 0.6, resized_img, 0.4, 0, resized_img)
                self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="Bounding box picked!")
            
        # Step 3: Convert the image from BGR to RGB
        resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

        # Step 4: Convert the NumPy array to a PIL Image
        pil_img = Image.fromarray(resized_img)

        # Step 5: Convert the PIL Image to a Tkinter PhotoImage
        self.image = ImageTk.PhotoImage(pil_img)
        self.labels["Image"].config(image=self.image)
        
    def readPersonName(self) -> None:
        """
        Reads and extracts the person's name from the file path stored in the data structure.
        This method parses the file path associated with the current person index and sub-index,
        extracts the name by splitting the path, and replaces underscores with spaces. The extracted
        name is then displayed in the "Name" label of the "Person_info_frame".
        Attributes:
            self.parsed_path (list): A list of path components obtained by splitting the file path.
            self.name (str): The extracted and formatted name of the person.
        Updates:
            Updates the "Name" label in the "Person_info_frame" with the extracted name.
        """
        self.parsed_path = self.data[self.person_index][self.person_sub_index]["path"].split("/")
        
        self.name = self.parsed_path[2].replace("_", " ")
        self.labels["Person_info_frame"]["Name"].config(text = self.name)

    def setAnnotationStatus(self) -> None:
        """
        Sets the annotation status label to one of the following:
        unnanotated/ partialy annotated/ fully annotated
        """
        # Find out the annotation status:
        status, color ="", ""
        if self.data_from_annotation[self.person_index] == []:
            status, color = "unnanotated", "red"
        else:
            present = False
            img_path = self.data[self.person_index][self.person_sub_index]["path"]
            for img in self.data_from_annotation[self.person_index]:
                if img["path"] == img_path:
                    present = True
                    break
            if present and self.data_from_annotation[self.person_index][self.person_sub_index]["fully_annotated"]:
                status, color = "fully annotated", "green"
            elif present:
                status, color = "partially annotated", "orange"
            else:
                status, color = "unnnanotated", "red"
            
        # set the annotation status on the front end:
        self.labels["Annotation_status"].config(text = status, foreground = color)

    def readPersonID(self) -> None:
        """
        Sets the Person's ID in the GUI.
        ID is self.person_index.
        """
        self.labels["Person_id"].config(text = self.person_index)

    def readAnnotationPercentage(self) -> None:
        """
        Sets the number of already annotated in the GUI.
        """
        all = len(self.data_from_annotation)
        anotated  = all - self.data_from_annotation.count([]) # number of annotated images
        self.labels["Annotation_percentage"].config(text = str(anotated)+ " / " + str(all) )
        #perc = 100 * (len(self.data_from_annotation) - n)/len(self.data_from_annotation)
        #self.labels["Annotation_percentage"].config(text = str( round(perc,2)) + " %") 

    def readPersonBirthDate(self) -> None:
        """
        Updates the birth date information (day, month, and year) for a person 
        in the user interface by extracting and processing data from a file path.
        This method:
        - Extracts the file path from the `self.data` structure based on the 
          current `person_index` and `person_sub_index`.
        - Processes the file path to determine the birth year using the 
          `find_birth_year` function.
        - Updates the corresponding comboboxes in the "Person_info_frame" 
          with the extracted birth day, month, and year.
        If the birth year cannot be determined, it sets the year combobox to an 
        empty string.
        Returns:
            None
        """
        path = self.data[self.person_index][self.person_sub_index]["path"].split("/")
        path = "./" + path[1] + "/" + path[2]
        path = Path(path)
        
        self.birth_day = ""
        self.comboboxes["Person_info_frame"]["Birth"]["Day"].set(str(self.birth_day))
        
        self.birth_month = ""
        self.comboboxes["Person_info_frame"]["Birth"]["Month"].set(self.birth_month)
        
        self.birth_year = str(find_birth_year(path))
        
        if self.birth_year == "None":
            self.birth_year = ""
            
        self.comboboxes["Person_info_frame"]["Birth"]["Year"].set(str(self.birth_year))
    
    def readWikiLink(self) -> None:
        """
        Reads the Wikipedia link for the current person and stores it in the `self.link` attribute.
        The method retrieves the URL from the `self.data` structure based on the current
        `person_index` and `person_sub_index` values.
        Attributes:
            self.link (str): The Wikipedia URL for the current person.
        """
        
        self.link = self.data[self.person_index][self.person_sub_index]["url"]
            
    def openWiki(self, event, link: str) -> None:
        """
        Opens a Wikipedia link in a separate process using multiprocessing.
        Args:
            event: The event object triggering this method (e.g., a GUI event).
            link (str): The URL of the Wikipedia page to open.
        Returns:
            None
        """
        if self.web_mode == "webbrowser":
            webbrowser.open(link)
        elif self.web_mode == "pywebview":
            self.web_proc = multiprocessing.Process(target=multiProcessWeb, args=(link,))
            self.web_proc.start()

    def readWikiParagraph(self) -> None:
        """
        Displays the first paragraph of the person's wiki page in the GUI.
        """
        # get the text:
        char_limit = 300
        path_to_person = Path( (self.data[self.person_index][0]["path"].rsplit("/",2))[0] )    # get only the path to the person folder
        try:
            with open(path_to_person / "text.txt", "r", encoding='UTF-8') as f:
                wikiText = f.read()[:char_limit]
            if wikiText == "":
                wikiText = "File with Wikipedia text is empty."
        except FileNotFoundError:
            wikiText = "File with Wikipedia text not found."

        # set it in the GUI:
        self.texts["First_paragraph"].config(state="normal")
        self.texts["First_paragraph"].delete("1.0", "end")
        self.texts["First_paragraph"].insert("1.0", wikiText)
        self.texts["First_paragraph"].config(state="disabled")

    def printPixelPosition(self, event) -> None:
        """
        Handles the event of a mouse click on an image, determines the pixel position
        of the click, checks if the click falls within any bounding boxes, and updates
        the GUI accordingly.
        Args:
            event: The event object containing information about the mouse click,
                   including the x and y coordinates.
        Behavior:
            - Calculates the pixel position of the click relative to the scaling factor.
            - Loads the image and resizes it based on the scaling factor.
            - Iterates through the bounding boxes associated with the current image.
            - Highlights the bounding box if the click falls within it.
            - Updates the GUI label to indicate whether no bounding box, one bounding box,
              or multiple bounding boxes were selected.
            - Updates the displayed image with the highlighted bounding box (if any).
        Notes:
            - The method assumes that `self.data` contains the image paths and bounding
              box information.
            - The `self.labels` dictionary is used to update GUI elements.
            - The `self.scaling_factor` is used to scale the image and bounding boxes.
            - The `self.bounding_box_index` is updated to the index of the selected
              bounding box if exactly one is selected, otherwise set to None.
        """
        
        x, y = event.x, event.y
        pixel_position = (int(x/self.scaling_factor), int(y/self.scaling_factor))
        self.person_pixel_position = pixel_position
        img = imread_unicode(self.data[self.person_index][self.person_sub_index]["path"])
        h, w = img.shape[:2]
        resized_img = cv2.resize(img, (int(w*self.scaling_factor), int(h*self.scaling_factor)), interpolation=cv2.INTER_AREA)
        cnt = 0
        
        for i in range(len(self.data[self.person_index][self.person_sub_index]["bbox_info"])):
            bbox = self.data[self.person_index][self.person_sub_index]["bbox_info"][i]
            #cv2.rectangle(resized_img, (int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)),
            #              (int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)), (0, 255, 0), 3)
            cv2.polylines(resized_img, [np.array([[int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)],
                                                  [int(bbox[2]*self.scaling_factor), int(bbox[3]*self.scaling_factor)],
                                                  [int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)],
                                                  [int(bbox[6]*self.scaling_factor), int(bbox[7]*self.scaling_factor)]],np.int32)], color=(0, 255, 0), isClosed=True, thickness=3)
            if self.checkbuttons["Face"].instate(["selected"]):
                if(pixel_position[0] >= bbox[0] and pixel_position[0] <= bbox[4] and 
                    pixel_position[1] >= bbox[1] and pixel_position[1] <= bbox[5]):
                    overlay = resized_img.copy()
                    cnt += 1
                    self.bounding_box_index = i
                    #cv2.rectangle(overlay, (int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)),
                    #              (int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)), (0, 255, 0), thickness=-1)
                    cv2.fillPoly(resized_img, [np.array([[int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)],
                                                        [int(bbox[2]*self.scaling_factor), int(bbox[3]*self.scaling_factor)],
                                                        [int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)],
                                                        [int(bbox[6]*self.scaling_factor), int(bbox[7]*self.scaling_factor)]],np.int32)], color=(0, 255, 0))
                    cv2.addWeighted(overlay, 0.6, resized_img, 0.4, 0, resized_img)
        
        if self.checkbuttons["Face"].instate(["selected"]) == False:
            self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="No correct bounding box!")
            self.bounding_box_index = None
        elif cnt == 0:
            self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="Bounding box not picked!")
        elif cnt == 1:
            self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text=f"Bounding box picked!")
        else:
            self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="Pick single bounding box!")
            self.bounding_box_index = None
        
        # Draw a single point at the clicked position
        cv2.circle(resized_img, (x, y), radius=10, color=(0, 0, 255), thickness=-1)
        resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(resized_img)
        self.image = ImageTk.PhotoImage(pil_img)
        self.labels["Image"].config(image=self.image)
     
    def openPopup(self, reference_errors: list, error_vals: list) -> None:
        """
        Opens a popup window to display a list of error messages.
        Args:
            reference_errors (list): A list of error messages to display in the popup.
            error_vals (list): A list of boolean values indicating whether to display 
                               the corresponding error message from `reference_errors`.
        Returns:
            None
        """
        # Create a new popup window (Toplevel)
        popup = tb.Toplevel(self)
        popup.title("Error")
        popup_width = 800
        popup_height = 400
        
        # Make the popup modal (optional)
        popup.grab_set()
        
        # Get the main window's position and size
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        
        # Calculate coordinates for centering the popup
        pos_x = main_x + (main_width // 2) - (popup_width // 2)
        pos_y = main_y + (main_height // 2) - (popup_height // 2)
        
        # Set the new geometry with the calculated coordinates
        
        popup.geometry(f"+{pos_x}+{pos_y}")

        # Add a label and a close button to the popup
        for i in range(len(reference_errors)):
            if error_vals[i]:
                label = tb.Label(popup, text=reference_errors[i])
                label.pack(padx=20, pady=5, anchor="w")
        
        close_button = tb.Button(popup, text="Close", bootstyle = tb.DANGER, command=popup.destroy, takefocus=False)
        close_button.pack(pady=10)
    
    def estimatedYearCreationCopy(self,event) -> None:
        """
        Copies the value from the "Year_left" combobox to the "Year_right" combobox
        within the "Image_creation_frame_plus_pixel_pos" group.
        Args:
            event: The event object triggered by the user interaction.
        """
        
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].set(self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].get())
    
    def loadAlreadyAnnotated(self) -> None:
        """
        After restarting the annotation tool, load the data from already annotated jsons into
        self.data_from_annotation. Assumes catRelatedImages() has already been executed. 
        """
        self.data_from_annotation = [[] for i in range(len(self.data))]

        for i in range( len(self.data) ):
            path_to_person = Path( (self.data[i][0]["path"].rsplit("/",2))[0] )    # get only the path to the person folder
            path_to_annotation = path_to_person / "annotation.json"
            try:
                with open(path_to_annotation, 'r') as f:
                    self.data_from_annotation[i] = json.load(f)
            except FileNotFoundError:
                continue
        
        self.fillDataToAnnotationWidgets()      # to fill the annotation of the first image

    def getDataFromAnnotation(self) -> None:
        """
        Extracts annotation data from the GUI components and updates the internal data structure.
        This method retrieves user-provided annotation data from various GUI elements, processes it,
        and stores it in the `data_from_annotation` attribute. It ensures that the data structure
        is initialized if not already done and updates or appends the annotation data for the
        currently selected person and sub-index.
        Returns:
            None
        Attributes Used:
            - self.data_from_annotation: A list of lists storing annotation data for each person.
            - self.data: A list containing metadata for each person, including file paths.
            - self.comboboxes: A dictionary of combobox widgets for user input.
            - self.checkbuttons: A dictionary of checkbutton widgets for user input.
            - self.texts: A dictionary of text widgets for user input.
            - self.bounding_box_index: An integer representing the index of the bounding box.
            - self.person_index: An integer representing the index of the current person.
            - self.person_sub_index: An integer representing the sub-index of the current person.
        GUI Inputs Processed:
            - Birth day, month, and year from comboboxes.
            - Estimated year of image creation (left and right) from comboboxes.
            - Checkbutton states for birthday, figure year, and face annotations.
            - Annotation shortcomings from a text widget.
        Data Stored:
            - A dictionary containing:
                - `path`: File path of the image.
                - `fully_annotated`: Boolean indicating if all annotations are complete.
                - `birthday_annotated`: Boolean indicating if the birthday is annotated.
                - `figure_year_annotated`: Boolean indicating if the figure year is annotated.
                - `face_found`: Boolean indicating if a face is found.
                - `birth_day`: Day of birth.
                - `birth_month`: Month of birth (converted to integer).
                - `birth_year`: Year of birth.
                - `estimated_year_creation_left`: Estimated year of creation (left).
                - `estimated_year_creation_right`: Estimated year of creation (right).
                - `annotation_shortcommings`: Text describing annotation shortcomings.
                - `bounding_box_index`: Index of the bounding box.
        Notes:
            - The method converts the birth month from a string to an integer index (1-based).
            - If the `data_from_annotation` list for the current person index is shorter than
              the sub-index, the data dictionary is appended; otherwise, it is updated.
        """
    
        months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        
        # get data from the GUI:
        birth_day = self.comboboxes["Person_info_frame"]["Birth"]["Day"].get()
        birth_month = self.comboboxes["Person_info_frame"]["Birth"]["Month"].get()
        if birth_month.lower() in months:
            birth_month = months.index(birth_month.lower()) + 1
        birth_year = self.comboboxes["Person_info_frame"]["Birth"]["Year"].get()
        estimated_year_creation_left = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].get()
        estimated_year_creation_right = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].get()
        birthday_checkbox = self.checkbuttons["Birth"].instate(["selected"])
        figure_checkbox = self.checkbuttons["Creation"].instate(["selected"])
        face_checkbox = self.checkbuttons["Face"].instate(["selected"])
        wiki_sufficient_checkbox = self.checkbuttons["Wiki_page_sufficient_for_annotation"].instate(["selected"])
        anootation_shortcommings = self.texts["Pos_to_annote"].get("1.0", "end")
        bounding_box_index = self.bounding_box_index
        path = self.data[self.person_index][self.person_sub_index]["path"]

        # write data in a dict (will also be used for json creation):
        dataDict = {"path": path,
                    "person_id": self.person_index,
                    "fully_annotated": birthday_checkbox and figure_checkbox and face_checkbox,
                    "birthday_annotated": birthday_checkbox,
                    "figure_year_annotated": figure_checkbox,
                    "face_found": face_checkbox,
                    "wiki_page_sufficient": wiki_sufficient_checkbox,
                    "birth_day": birth_day,
                    "birth_month": birth_month,
                    "birth_year": birth_year,
                    "estimated_year_creation_left": estimated_year_creation_left,
                    "estimated_year_creation_right": estimated_year_creation_right,
                    "annotation_shortcommings": anootation_shortcommings,
                    "bounding_box_index": bounding_box_index,
                    "face_pixel_coordinates": self.person_pixel_position}

        # append the dict into self.data_from_annotation
        if len(self.data_from_annotation[self.person_index]) > self.person_sub_index:
            self.data_from_annotation[self.person_index][self.person_sub_index] = dataDict
        else:
            self.data_from_annotation[self.person_index].append(dataDict)
             
    def removeDataFromAnnotationWidgets(self) -> None:
        """
        Clears and resets the annotation widgets and related states.
        This method performs the following actions:
        - Resets the values of various comboboxes related to birth and image creation.
        - Clears and disables the text widget for annotation positions.
        - Updates the label text to prompt the user to click on the image.
        - Resets flags indicating whether annotation is possible for birth, creation, and face.
        - Resets the bounding box index to None.
        Behavior differs based on the value of `self.person_sub_index`:
        - If `self.person_sub_index` is 0:
            - Resets additional comboboxes related to birth information (Day, Month, Year).
        - Otherwise:
            - Only resets comboboxes related to image creation.
        This method ensures that the annotation interface is cleared and ready for new input.
        """
        if self.person_sub_index == 0:
            self.comboboxes["Person_info_frame"]["Birth"]["Day"].set("")
            self.comboboxes["Person_info_frame"]["Birth"]["Month"].set("")
            self.comboboxes["Person_info_frame"]["Birth"]["Year"].set("")

        # always:
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].set("")
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].set("")
        self.possible_to_annotate_birth.set(1)
        self.possible_to_annotate_creation.set(1)
        self.possible_to_annotate_face.set(1)
        self.possible_to_annotate_sufficient.set(1)
        self.texts["Pos_to_annote"].config(state="normal")
        self.texts["Pos_to_annote"].delete("1.0", "end")
        self.texts["Pos_to_annote"].config(state="disabled")
        self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="Click on the image")
        self.bounding_box_index = None
    
    def fillDataToAnnotationWidgets(self) -> None:
        """
        Populates the annotation widgets with data from the current annotation entry.
        This method retrieves annotation data for the currently selected person and 
        sub-index from `self.data_from_annotation` and updates the corresponding 
        widgets in the GUI. It sets values for birth date, estimated year of image 
        creation, annotation shortcomings, and bounding box status.
        Updates:
            - Comboboxes for birth day, month, and year.
            - Comboboxes for estimated year of image creation (left and right).
            - A text widget for annotation shortcomings.
            - A label indicating whether a bounding box was picked.
            - A variable indicating if the annotation is impossible to complete.
        Behavior:
            - If a bounding box index is present, updates the label to indicate 
              that a bounding box was picked.
            - If no bounding box index is present, updates the label to prompt 
              the user to click on the image.
        Args:
            None
        Returns:
            None
        """
        if self.data_from_annotation[self.person_index] != []:
            birth_day = self.data_from_annotation[self.person_index][self.person_sub_index]["birth_day"]
            birth_month = self.data_from_annotation[self.person_index][self.person_sub_index]["birth_month"]
            birth_year = self.data_from_annotation[self.person_index][self.person_sub_index]["birth_year"]
            estimated_year_creation_left = self.data_from_annotation[self.person_index][self.person_sub_index]["estimated_year_creation_left"]
            estimated_year_creation_right = self.data_from_annotation[self.person_index][self.person_sub_index]["estimated_year_creation_right"]
            annotation_shortcommings = self.data_from_annotation[self.person_index][self.person_sub_index]["annotation_shortcommings"]
            self.bounding_box_index = self.data_from_annotation[self.person_index][self.person_sub_index]["bounding_box_index"]
            
            self.comboboxes["Person_info_frame"]["Birth"]["Day"].set(birth_day)
            self.comboboxes["Person_info_frame"]["Birth"]["Month"].set(birth_month)
            self.comboboxes["Person_info_frame"]["Birth"]["Year"].set(birth_year)
            self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].set(estimated_year_creation_left)
            self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].set(estimated_year_creation_right)
            self.possible_to_annotate_birth.set(self.data_from_annotation[self.person_index][self.person_sub_index]["birthday_annotated"])
            self.possible_to_annotate_creation.set(self.data_from_annotation[self.person_index][self.person_sub_index]["figure_year_annotated"])
            self.possible_to_annotate_face.set(self.data_from_annotation[self.person_index][self.person_sub_index]["face_found"])
            self.possible_to_annotate_sufficient.set(self.data_from_annotation[self.person_index][self.person_sub_index]["wiki_page_sufficient"])
            self.texts["Pos_to_annote"].config(state="normal")
            self.texts["Pos_to_annote"].delete("1.0", "end")
            self.texts["Pos_to_annote"].insert("1.0", annotation_shortcommings)
            self.texts["Pos_to_annote"].config(state="disabled")
            if self.bounding_box_index != None:
                self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="Bounding box was picked!")
            else:
                self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="Click on the image")

    def write_annot_to_json(self):
        """
        Writes the annotation of the current image to the database.
        """
        image_annotation = self.data_from_annotation[self.person_index][self.person_sub_index]
        pathstring = (image_annotation["path"].rsplit("/",2))[0]      # get only the path to the person folder
        path_to_annotation = Path(pathstring) / "annotation.json"

        # try to open and read the person's annotation file
        try:
            with open(path_to_annotation, 'r') as f:
                jsonData = json.load(f)
        except FileNotFoundError:
            jsonData = []  

        # if annotation.json has older image annotation, delete it: 
        if jsonData != []:
            idx = None
            for i in range( len(jsonData) ):
                if jsonData[i]["path"] == image_annotation["path"]:
                    idx = i
                    break
            if idx != None:
                jsonData.pop(idx)

        # append the new annotation to jsonData:
        jsonData.append(image_annotation)

        with open(path_to_annotation , "w") as f:
            json.dump(jsonData, f, indent=4)

    def saveAnnotation(self) -> None:
        """
        Saves the image annotation to json. Includes pop-up window check.
        """
        list_of_errors = ["Birth day is not filled or is not an integer in the range 1-31!",
                          "Birth month is not filled or is not an integer in the range 1-12 or its name is written incorrectly!",
                          "Birth year is not filled or is not an integer lower than the current year!",
                          "Estimated year of image creation (left boundary) is not filled or is not an integer lower than the current year!",
                          "Estimated year of image creation (right boundary) is not filled or is not an integer lower than the current year!",
                          "Estimated year of image creation (right boundary) is lower than its (left boundary)!",
                          "Bounding box was not picked or multiple bounding boxes were picked!",
                          "Annotation shortcomings are not specified."]
        
        list_of_errors_vals = [False for i in range(len(list_of_errors))]
        list_of_month_names = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        
        birth_day = self.comboboxes["Person_info_frame"]["Birth"]["Day"].get()
        birth_month = self.comboboxes["Person_info_frame"]["Birth"]["Month"].get()
        birth_year = self.comboboxes["Person_info_frame"]["Birth"]["Year"].get()
        estimated_year_creation_left = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].get()
        estimated_year_creation_right = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].get()
        bounding_box = self.bounding_box_index
        creation_checked, birth_checked, face_checked = (self.checkbuttons["Creation"].instate(["selected"]),
                                                        self.checkbuttons["Birth"].instate(["selected"]),
                                                        self.checkbuttons["Face"].instate(["selected"]))

        #if birth_checked and (not birth_day.isdigit() or int(birth_day) not in range(1,32)):
        #    list_of_errors_vals[0] = True
        #if birth_checked and (not birth_month.isdigit() and birth_month.lower() not in list_of_month_names):
        #    list_of_errors_vals[1] = True
        #if birth_checked and (birth_month.isdigit() and int(birth_month) not in range(1,13)):
        #    list_of_errors_vals[1] = True
        if birth_checked and (not birth_year.isdigit() or int(birth_year) not in range(datetime.date.today().year + 1)):
            list_of_errors_vals[2] = True
        if creation_checked and (estimated_year_creation_left == "" or not estimated_year_creation_left.isdigit() or int(estimated_year_creation_left) not in range(datetime.date.today().year + 1)):
            list_of_errors_vals[3] = True
        if creation_checked and (estimated_year_creation_right == "" or not estimated_year_creation_right.isdigit() or int(estimated_year_creation_right) not in range(datetime.date.today().year + 1)):
            list_of_errors_vals[4] = True
        if creation_checked and (estimated_year_creation_left.isdigit() and estimated_year_creation_right.isdigit() and int(estimated_year_creation_right) < int(estimated_year_creation_left)):
            list_of_errors_vals[5] = True
        if face_checked and bounding_box == None:
            list_of_errors_vals[6] = True
        all_selected = (birth_checked and creation_checked and face_checked)
        if not all_selected and not self.texts["Pos_to_annote"].get("1.0", "end-1c").strip():    # checks is ScrolledText is empty 
            list_of_errors_vals[7] = True

        if any(list_of_errors_vals) and (all_selected):
            self.openPopup(list_of_errors, list_of_errors_vals)
        elif not all_selected and any(list_of_errors_vals):
            self.openPopup(list_of_errors, list_of_errors_vals)
        else:
            self.getDataFromAnnotation()
            self.write_annot_to_json()

        self.setAnnotationStatus()
        self.readAnnotationPercentage()

    def loadRecord(self) -> None:
        """
        Loads the record with the current person_index and person_subindex into
        the GUI.
        """
        path_to_person = Path( (self.data[self.person_index][0]["path"].rsplit("/",2))[0] )
        print( path_to_person)
        self.entries["Control_panel"]["LEFT"].config(state="normal")
        self.entries["Control_panel"]["LEFT"].delete(0, "end")
        self.entries["Control_panel"]["LEFT"].insert(0, str(self.person_sub_index + 1))
        self.entries["Control_panel"]["LEFT"].config(state="readonly")
        
        self.entries["Control_panel"]["RIGHT"].config(state="normal")
        self.entries["Control_panel"]["RIGHT"].delete(0, "end")
        self.entries["Control_panel"]["RIGHT"].insert(0, str(len(self.data[self.person_index])))
        self.entries["Control_panel"]["RIGHT"].config(state="readonly")
        
        if len(self.data_from_annotation[self.person_index]) > self.person_sub_index:      # if annotation for this picture already exists
            self.fillDataToAnnotationWidgets()
        else:
            self.removeDataFromAnnotationWidgets()
            self.readPersonBirthDate()
            if self.person_index > 0 and len(self.data_from_annotation[self.person_index]) > 0:
                # if this is a consecutive photo of the same person and some annotation of this personn already exists
                idx = 0
                for i in range( len(self.data_from_annotation[self.person_index])):
                    if self.data_from_annotation[self.person_index][i] != []:
                        idx = i
                        date_of_birth = str(self.data_from_annotation[self.person_index][i]["birth_day"])
                        if date_of_birth.isdigit():
                            # the actual saved birth day and month are found now, end search
                            break
                birth_day = self.data_from_annotation[self.person_index][idx]["birth_day"]
                birth_month = self.data_from_annotation[self.person_index][idx]["birth_month"]
                birth_year = self.data_from_annotation[self.person_index][idx]["birth_year"]
                self.comboboxes["Person_info_frame"]["Birth"]["Day"].set(birth_day)
                self.comboboxes["Person_info_frame"]["Birth"]["Month"].set(birth_month)
                self.comboboxes["Person_info_frame"]["Birth"]["Year"].set(birth_year)
            
        self.readCaption()
        self.readImage()
        self.readPersonName()
        self.readWikiLink()
        self.setAnnotationStatus()
        self.readPersonID()
        self.readAnnotationPercentage()
        self.readWikiParagraph()
        
        if self.web_proc != None:
            self.web_proc.terminate()
            self.web_proc.join()

    def nextRecord(self) -> None:           # not being used curently !!! See nextRecordWithoutSaving()
        """
        Handles the transition to the next record in the annotation process.
        This method validates user inputs for various fields, checks for errors, 
        and either displays a popup with error messages or proceeds to process 
        the current annotation data. If the current record is the last one for 
        the person, it writes the data to a JSON file and moves to the next person. 
        Otherwise, it updates the interface to display the next record.
        Validation checks include:
        - Birth day is a valid integer in the range 1-31.
        - Birth month is either a valid integer in the range 1-12 or a valid month name.
        - Birth year is a valid integer less than or equal to the current year.
        - Estimated year of image creation (left and right boundaries) are valid integers 
          less than or equal to the current year.
        - The right boundary of the estimated year of image creation is not less than 
          the left boundary.
        - A bounding box is selected.
        If any validation errors are found and the "Pos_to_annote" checkbox is not selected, 
        a popup is displayed with the corresponding error messages.
        Otherwise, the method:
        - Retrieves data from the annotation widgets.
        - Updates the indices for the current person and record.
        - Updates the control panel entries to reflect the current record and total records.
        - Fills or clears annotation widgets based on the current record.
        - Reads and updates the caption, image, person info, and wiki link.
        - Terminates any running web process.
        Raises:
            None
        Returns:
            None
        Callbacks:
        - This method is typically bound to the "Next" (RIGHT) button in the GUI.
        """
        
        list_of_errors = ["Birth day is not filled or is not an integer in the range 1-31!",
                          "Birth month is not filled or is not an integer in the range 1-12 or its name is written incorrectly!",
                          "Birth year is not filled or is not an integer lower than the current year!",
                          "Estimated year of image creation (left boundary) is not filled or is not an integer lower than the current year!",
                          "Estimated year of image creation (right boundary) is not filled or is not an integer lower than the current year!",
                          "Estimated year of image creation (right boundary) is lower than its (left boundary)!",
                          "Bounding box was not picked or multiple bounding boxes were picked!",
                          "Annotation shortcomings are not specified."]
        
        list_of_errors_vals = [False for i in range(len(list_of_errors))]
        list_of_month_names = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        
        birth_day = self.comboboxes["Person_info_frame"]["Birth"]["Day"].get()
        birth_month = self.comboboxes["Person_info_frame"]["Birth"]["Month"].get()
        birth_year = self.comboboxes["Person_info_frame"]["Birth"]["Year"].get()
        estimated_year_creation_left = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].get()
        estimated_year_creation_right = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].get()
        bounding_box = self.bounding_box_index
        creation_checked, birth_checked, face_checked = (self.checkbuttons["Creation"].instate(["selected"]),
                                                        self.checkbuttons["Birth"].instate(["selected"]),
                                                        self.checkbuttons["Face"].instate(["selected"]))

        if birth_checked and (not birth_day.isdigit() or int(birth_day) not in range(1,32)):
            list_of_errors_vals[0] = True
        if birth_checked and (not birth_month.isdigit() and birth_month.lower() not in list_of_month_names):
            list_of_errors_vals[1] = True
        if birth_checked and (birth_month.isdigit() and int(birth_month) not in range(1,13)):
            list_of_errors_vals[1] = True
        if birth_checked and (not birth_year.isdigit() or int(birth_year) not in range(datetime.date.today().year + 1)):
            list_of_errors_vals[2] = True
        if creation_checked and (estimated_year_creation_left == "" or not estimated_year_creation_left.isdigit() or int(estimated_year_creation_left) not in range(datetime.date.today().year + 1)):
            list_of_errors_vals[3] = True
        if creation_checked and (estimated_year_creation_right == "" or not estimated_year_creation_right.isdigit() or int(estimated_year_creation_right) not in range(datetime.date.today().year + 1)):
            list_of_errors_vals[4] = True
        if creation_checked and (estimated_year_creation_left.isdigit() and estimated_year_creation_right.isdigit() and int(estimated_year_creation_right) < int(estimated_year_creation_left)):
            list_of_errors_vals[5] = True
        if face_checked and bounding_box == None:
            list_of_errors_vals[6] = True
        all_selected = (birth_checked and creation_checked and face_checked)
        if not all_selected and not self.texts["Pos_to_annote"].get("1.0", "end-1c").strip():    # checks is ScrolledText is empty 
            list_of_errors_vals[7] = True

        if any(list_of_errors_vals) and (all_selected):
            self.openPopup(list_of_errors, list_of_errors_vals)
        elif not all_selected and any(list_of_errors_vals):
            self.openPopup(list_of_errors, list_of_errors_vals)
        else:
            self.getDataFromAnnotation()
            
            if(self.person_sub_index + 1 == len(self.data[self.person_index])):
                self.write_annot_to_json()     # write data to JSON
                self.person_index += 1
                self.person_sub_index = 0
            else:
                self.write_annot_to_json()  # write data to JSON
                self.person_sub_index += 1
            
            self.loadRecord()
    
    def nextRecordWithoutSaving(self) -> None:
        """
        Like nextRecord(), but does not save the annotation neither does it trigger the
        warning pop-up window.
        """
        if(self.person_sub_index + 1 == len(self.data[self.person_index])):
            self.person_index += 1
            self.person_sub_index = 0
        else:
            self.person_sub_index += 1
        
        self.loadRecord()

    def previousRecord(self) -> None:
        """
        Navigate to the previous record in the dataset and update the GUI accordingly.
        This method adjusts the indices for navigating through a dataset of records.
        It updates the control panel GUI elements to reflect the current record's position
        and total count. Additionally, it populates annotation widgets with the current
        record's data and performs cleanup of any running web processes.
        Steps performed:
        1. Adjusts `person_index` and `person_sub_index` to point to the previous record.
        2. Updates the "LEFT" and "RIGHT" control panel entries to display the current
           record index and total records for the current person.
        3. Calls helper methods to populate annotation widgets and load associated data:
           - `fillDataToAnnotationWidgets()`
           - `readCaption()`
           - `readImage()`
           - `readPersonName()`
           - `readWikiLink()`
        4. Terminates and joins any running web process (`web_proc`) if it exists.
        Note:
        - The method assumes `self.data` is a list of records grouped by person.
        - The control panel entries are assumed to be part of a dictionary `self.entries`.
        Raises:
        - No explicit exceptions are raised, but errors may occur if the indices are
          out of bounds or if the UI elements are not properly initialized.
        Callbacks:
        - This method is bound to the "LEFT" button in the control panel to navigate to the previous record.
        """
        if(self.person_sub_index == 0):
            if(self.person_index != 0):
                self.person_index -= 1
                self.person_sub_index = len(self.data[self.person_index]) - 1
        else:
            self.person_sub_index -= 1
        
        self.loadRecord()
    
    def skipToFirstUnannotated(self) -> None:
        """
        Skips to the first unannotated item in the dataset.
        This method is intended to locate and navigate to the first item
        in the dataset that has not yet been annotated. The specific behavior
        and implementation details depend on the structure of the dataset
        and the annotation logic.
        Returns:
            None
        """
        # figure out what is the first unanotated image:
        idx, subIdx = 0, 0
        if [] in self.data_from_annotation:
            first_empty = self.data_from_annotation.index([])
            if first_empty != 0:
                annotated = len(self.data_from_annotation[first_empty - 1])
                all = len(self.data[first_empty - 1])
                if annotated != all:
                    idx = first_empty - 1
                    subIdx = annotated
                else:
                    idx = first_empty
            self.person_index = idx
            self.person_sub_index = subIdx
        else:
            self.person_index = len(self.data_from_annotation) - 1
        
        # config the front end:
        self.loadRecord()
    
    def checkbuttonsKeyPress(self, event) -> None:
        """
        Handles key press events for checkbuttons in the annotation tool.
        This method is triggered when a key is pressed while a checkbutton is focused.
        It checks if the pressed key is 'b' or 'c' and toggles the corresponding checkbutton
        state (Birth or Creation) accordingly. The event is passed as an argument to the method.
        Args:
            event: The key press event object containing information about the pressed key.
        Returns:
            None
        """
        if isinstance(event.widget, tb.ScrolledText) or isinstance(event.widget, tb.Combobox):
            return None        
        
        if event.char == "e":
            if self.checkbuttons["Birth"].instate(["selected"]):
                self.possible_to_annotate_birth.set(0)
            else:
                self.possible_to_annotate_birth.set(1)
        elif event.char == "r":
            if self.checkbuttons["Creation"].instate(["selected"]):
                self.possible_to_annotate_creation.set(0)
            else:
                self.possible_to_annotate_creation.set(1)
        elif event.char == "t":
            if self.checkbuttons["Face"].instate(["selected"]):
                self.possible_to_annotate_face.set(0)
            else:
                self.possible_to_annotate_face.set(1)
        elif event.char == "q":
            if self.checkbuttons["Wiki_page_sufficient_for_annotation"].instate(["selected"]):
                self.possible_to_annotate_sufficient.set(0)
            else:
                self.possible_to_annotate_sufficient.set(1)
        
        self.possToFullyAnnotateCallback()
        self.possToFullyAnnotateFace()
        
    def defaultScreenBuild(self):
        """
        Constructs and configures the default screen layout for the application.
        This method sets up the grid layout, places various frames, labels, text widgets,
        comboboxes, buttons, and other UI elements in their respective positions. It also
        initializes and updates the content of these widgets, such as images, captions,
        person information, and control panel widgets.
        Key functionalities:
        - Configures the grid layout for rows and columns with appropriate weights and sizes.
        - Places and updates the left-hand frames, including the image and caption frames.
        - Places and updates the right-hand frames, including person info, image creation,
          pixel position, control panel, and annotation-related frames.
        - Updates and binds events to widgets, such as image click events and combobox selections.
        - Reads and displays data such as captions, images, person information, and Wikipedia links.
        - Configures control panel widgets for navigation and annotation-related functionalities.
        Note:
        - This method assumes that the `self.frames`, `self.labels`, `self.texts`, `self.comboboxes`,
          `self.checkbuttons`, `self.buttons`, and `self.entries` dictionaries are pre-initialized
          with the required widgets.
        - The method also assumes that helper methods like `readCaption`, `readImage`, `readPersonName`,
          readPersonBirth() and `readWikiLink` are implemented to fetch and update the respective data.
        """
        # Set the layout of the main window
        self.update()
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, minsize = int(self.winfo_width()/3), weight=1)
        self.grid_columnconfigure(1, minsize = int(self.winfo_width()/2), weight=1)
        #--------------------------------------------------------------------------------------------
        
        #Place and configure main frames
        
        # LEFT frames
        self.frames["Image"].grid(row=0, column=0, rowspan = 5, sticky="nsew", padx=10, pady=40)
        self.frames["Caption"].grid(row=5, column=0, sticky="ew", padx=27, pady=10, ipady=10)
        
        # RIGHT frames
        
        #Name frame
        self.frames["Name"].grid_rowconfigure(0, weight=1)
        self.frames["Name"].grid_columnconfigure(0, weight=1)
        self.frames["Name"].grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        # Database info frame
        self.frames["Database_info"].grid_rowconfigure(0, weight=1)
        self.frames["Database_info"].grid_columnconfigure(0, weight=1)
        self.frames["Database_info"].grid_columnconfigure(1, weight=1)
        self.frames["Database_info"].grid_columnconfigure(2, weight=1)
        self.frames["Database_info"].grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        
        #First paragraph frame
        self.frames["First_paragraph"].grid_rowconfigure(0, weight=1)
        self.frames["First_paragraph"].grid_columnconfigure(0, weight=1)
        self.frames["First_paragraph"].grid(row=2, column=1, sticky="ew", padx=10, pady=10, ipady=10)
        
        #Birth and wiki link frames
        self.frames["Person_info_frame"]["MAIN"].grid_rowconfigure(0, weight=1)
        self.frames["Person_info_frame"]["MAIN"].grid_rowconfigure(1, weight=1)
        self.frames["Person_info_frame"]["MAIN"].grid_columnconfigure(0, weight=15)
        self.frames["Person_info_frame"]["MAIN"].grid_columnconfigure(1, weight=1)
        self.frames["Person_info_frame"]["MAIN"].grid_columnconfigure(2, weight=5)
        self.frames["Person_info_frame"]["MAIN"].grid(row=3, column=1, sticky="ew", padx=10, pady=10)      
        
        #Annotation shortcomings frame
        self.frames["Annotation_fail"].grid_rowconfigure(0, weight=1)
        self.frames["Annotation_fail"].grid_columnconfigure(0, weight=1)
        self.frames["Annotation_fail"].grid(row=4, column=1, sticky="ew", padx=10, pady=10, ipady=10)
        
        #Control panel frame
        self.frames["Control_panel"].grid_rowconfigure(0, weight=1)
        self.frames["Control_panel"].grid_columnconfigure(0, weight=10)
        self.frames["Control_panel"].grid_columnconfigure(1, weight=10)
        self.frames["Control_panel"].grid_columnconfigure(2, weight=1)
        self.frames["Control_panel"].grid_columnconfigure(3, weight=1)
        self.frames["Control_panel"].grid_columnconfigure(4, weight=1)
        self.frames["Control_panel"].grid_columnconfigure(5, weight=10)
        self.frames["Control_panel"].grid_columnconfigure(6, weight=10)
        self.frames["Control_panel"].grid(row=5, column=1, sticky="ew", padx=10, pady=10, ipady=11)
        #--------------------------------------------------------------------------------------------
        
        #Place subframes and configure them
        
        # RIGHT frames
        
        #Database info frame
        self.frames["Annotation_status"].grid_rowconfigure(0, weight=1)
        self.frames["Annotation_status"].grid_columnconfigure(0, weight=1)
        self.frames["Annotation_status"].grid(row=0, column=0, sticky="ew", padx=10, pady=0)
        
        self.frames["Person_id"].grid(row=0, column=1, sticky="ew", padx=10, pady=0)
        
        self.frames["Annotation_percentage"].grid(row=0, column=2, sticky="ew", padx=10, pady=0)
        
        #Wiki link frame and birth frame
        self.frames["Person_info_frame"]["Birth"].grid_rowconfigure(0, weight=1)
        self.frames["Person_info_frame"]["Birth"].grid_columnconfigure(0, weight=1)
        self.frames["Person_info_frame"]["Birth"].grid_columnconfigure(1, weight=1)
        self.frames["Person_info_frame"]["Birth"].grid_columnconfigure(2, weight=1)
        self.frames["Person_info_frame"]["Birth"].grid_columnconfigure(3, weight=1)
        self.frames["Person_info_frame"]["Birth"].grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
        
        self.frames["Person_info_frame"]["Wiki_link"].grid_rowconfigure(0, weight=1)
        self.frames["Person_info_frame"]["Wiki_link"].grid_columnconfigure(0, weight=1)
        self.frames["Person_info_frame"]["Wiki_link"].grid(row=0, column=0, sticky="nsew",pady=0)
        
        #Image creation and pixel position frames
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_rowconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(1, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(2, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(3, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(4, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(5, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid(row=1, column=2, sticky="nsew", padx=0, pady=20)
        
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"].grid_rowconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"].grid_columnconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"].grid_columnconfigure(1, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"].grid(row=1, column=0, sticky="nsew",pady=20)
        
        #Sufficient for annotation frame
        self.frames["Wiki_page_sufficient_for_annotation"].grid_rowconfigure(0, weight=1)
        self.frames["Wiki_page_sufficient_for_annotation"].grid_columnconfigure(0, weight=1)
        self.frames["Wiki_page_sufficient_for_annotation"].grid_columnconfigure(1, weight=1)
        self.frames["Wiki_page_sufficient_for_annotation"].grid(row=2, column=0, columnspan = 3, sticky="ns", padx=0, pady=0)
        #--------------------------------------------------------------------------------------------
        
        # Update and place the image and caption widgets
        
        self.readImage()
        self.labels["Image"].place(relx=0.5, rely=0.5, anchor="center")
        self.labels["Image"].bind("<Button-1>", self.printPixelPosition)
        
        self.readCaption()
        self.texts["Caption"].pack(fill="both", expand=True)
        self.texts["Caption"].insert("1.0", self.caption)
        self.texts["Caption"].config(state="disabled")
        #--------------------------------------------------------------------------------------------
        
        # Update and place the name 
        
        self.readPersonName()
        self.labels["Person_info_frame"]["Name"].grid(row=0, column=0, sticky="ns", padx=10)
        
        #--------------------------------------------------------------------------------------------
        
        # Update and place the database info widgets
        self.labels["Annotation_status"].grid(row=0, column=0, sticky="ns", padx=10)
        self.labels["Person_id"].grid(row=0, column=0, sticky="ns", padx=10)
        self.labels["Annotation_percentage"].grid(row=0, column=0, sticky="ns", padx=10)
        
        #---------------------------------------------------------------------------------------------
        # Update and place person info widgets
        self.labels["Wiki_page_sufficient_for_annotation"].grid(row=0, column=0, sticky="e", padx=10)
        
        self.checkbuttons["Wiki_page_sufficient_for_annotation"].grid(row=0, column=1, padx=0, sticky="w")
        self.bind("<KeyPress-q>", self.checkbuttonsKeyPress)
        
        #--------------------------------------------------------------------------------------------
        
        # Update and place birth and wiki link widgets
        
        #Birth frame
        self.readPersonBirthDate()
        self.comboboxes["Person_info_frame"]["Birth"]["Day"].grid(row=0, column=0, padx=0)
        self.comboboxes["Person_info_frame"]["Birth"]["Month"].grid(row=0, column=1, padx=0)
        self.comboboxes["Person_info_frame"]["Birth"]["Year"].grid(row=0, column=2, padx=0)
        
        self.checkbuttons["Birth"].grid(row=0, column=3, padx=0, sticky="e")
        self.bind("<KeyPress-e>", self.checkbuttonsKeyPress)
        
        #Wiki link frame
        self.readWikiLink()
        self.labels["Wiki_link"].grid(row=0, column=0, sticky="ew")
        self.labels["Wiki_link"].config(text = "Open Wikipedia page")
        self.labels["Wiki_link"].bind("<Button-1>", lambda k: self.openWiki(k,self.link))
        if(self.theme == "darkly"):
            self.labels["Wiki_link"].config(foreground = '#375a7f')
        #--------------------------------------------------------------------------------------------
        
        # Place and update the image creation frame and pixel position frame
        
        #Image creation frame
        self.labels["Image_creation_frame_plus_pixel_pos"]["("].grid(row=0, column=0, padx = 0)
        self.labels["Image_creation_frame_plus_pixel_pos"][";"].grid(row=0, column=2, padx= 0)
        self.labels["Image_creation_frame_plus_pixel_pos"][")"].grid(row=0, column=4, padx= 0)
        
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].grid(row=0, column=1, padx=0)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].bind("<<ComboboxSelected>>", self.estimatedYearCreationCopy)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].grid(row=0, column=3, padx=0)
        
        self.checkbuttons["Creation"].grid(row = 0, column = 5, padx = 0, sticky = "e")
        self.bind("<KeyPress-r>", self.checkbuttonsKeyPress)
        
        #Pixel position frame
        self.labels["Image_creation_frame_plus_pixel_pos"]["px"].grid(row=0, column=0, padx=0, sticky="nsew")
        
        self.checkbuttons["Face"].grid(row=0, column=1, sticky = "e")
        self.bind("<KeyPress-t>", self.checkbuttonsKeyPress)
        #--------------------------------------------------------------------------------------------
            
        # Update and place the control panel widgets
        self.buttons["Previous"].grid(row=0, column=0, padx=10)
        self.bind("<KeyPress-a>", lambda k: self.previousRecord() if not(isinstance(k.widget, tb.ScrolledText) or isinstance(k.widget, tb.Combobox)) else None)
        self.buttons["Save"].grid(row=0, column=1, padx=10)
        self.bind("<KeyPress-s>", lambda k: self.saveAnnotation() if not(isinstance(k.widget, tb.ScrolledText) or isinstance(k.widget, tb.Combobox)) else None)
        self.buttons["Skip_to_the_first_unannotated"].grid(row=0, column=5, padx=10)
        self.bind("<KeyPress-w>", lambda k: self.skipToFirstUnannotated() if not(isinstance(k.widget, tb.ScrolledText) or isinstance(k.widget, tb.Combobox)) else None)
        self.buttons["Next"].grid(row=0, column=6, padx=10)
        self.bind("<KeyPress-d>", lambda k: self.nextRecord() if not(isinstance(k.widget, tb.ScrolledText) or isinstance(k.widget, tb.Combobox)) else None)
        
        self.labels["Control_panel"]["/"].grid(row=0, column=3, padx=0)
        self.labels["Control_panel"]["/"].config(text="/")
        
        self.entries["Control_panel"]["LEFT"].grid(row=0, column=2, padx=0, sticky="e")
        self.entries["Control_panel"]["LEFT"].insert(0, str(self.person_sub_index + 1))
        self.entries["Control_panel"]["LEFT"].state(["readonly"])
        self.entries["Control_panel"]["RIGHT"].grid(row=0, column=4, padx=0, sticky="w")
        self.entries["Control_panel"]["RIGHT"].insert(0, str(len(self.data[self.person_index])))
        self.entries["Control_panel"]["RIGHT"].state(["readonly"])
        #--------------------------------------------------------------------------------------------
         
        # Update and place the annotation shortcomings widgets
        
        self.texts["Pos_to_annote"].grid(row=0, column=0, padx=10, sticky="nsew")
        self.texts["Pos_to_annote"].config(state="disabled")
        #--------------------------------------------------------------------------------------------
        
        # Update and place the first paragraph widgets
        
        self.texts["First_paragraph"].grid(row=0, column=0, padx=10, sticky="nsew")
        self.texts["First_paragraph"].config(state="disabled")
        
        
if __name__ == "__main__":
    multiprocessing.freeze_support() # Required for Windows
    std_args = sys.argv[1:]
    std_args_split = []
    
    for arg in std_args:
        if "=" in arg:
            temp = arg.split("=")
            std_args_split.append(temp[0] + "=")
            std_args_split.append(temp[1])
        else:
            std_args_split.append(arg)
    
    if "parser=on" in std_args:
        index = std_args.index("parser=on")
        try:
            if "=" not in std_args[index+1] and "=" not in std_args[index+2]:
                parse_dir = "./" + std_args[index+1] 
                parse_subset_name = std_args[index+2]
            else:
                parse_dir = None
            psr.parse_persons(parse_dir, write=True, parse_subset_name=parse_subset_name)
        except:
            print("[ERROR] There was an error while parsing the data!")
            print("[POSSIBLE SOLUTION] Check the name of the directory intended for parsing!")
            print("[POSSIBLE SOLUTION] Have you provide both the name of the directory and the name of the outputed .json file?")
            sys.exit(1)
        parsed_data_filename = "./" + parse_subset_name + ".json"
    else:
        if "data_json=" in std_args_split:
            index = std_args_split.index("data_json=")
            parsed_data_filename = std_args_split[index+1]+".json"
        else:
            parsed_data_filename = "./data1.json"     #TODO: Name of the json file containing the parser's output
                                                      #Change it if you are not running the anotaion tool from command line
    
    if "theme=" in std_args_split:
        index = std_args_split.index("theme=")
        print("Theme: ", std_args_split[index+1])
        if std_args_split[index+1] in ["dark", "light"]:
            if std_args_split[index+1] == "dark":
                theme = "darkly"
            else:
                theme = "cosmo"
        else:
            print("[ERROR] Theme should be either 'dark' or 'light'!")
            sys.exit(1)
    else:
        theme = "cosmo" #TODO: Change it if you are not running the anotaion tool from command line and you want to use darkly theme
    
    if "webview=" in std_args_split:
        index = std_args_split.index("webview=")
        if std_args_split[index+1] in ["pywebview", "webbrowser"]:
            web_mode = std_args_split[index+1]
        else:
            print("[ERROR] Web mode should be either 'pywebview' or 'webbrowser'!")
            sys.exit(1)
    else:
        web_mode = "pywebview"   #TODO: Change it if you are not running the anotaion tool from command line and you want to use webbrowser

    try: 
        app = AnnotationTool(parsed_data_json= parsed_data_filename, themename=theme, web_mode=web_mode)
        print(parsed_data_filename, theme, web_mode)
    except:
        print("[ERROR] Wrong name of the pre-parsed data file!")
        sys.exit(1)
        
    print("App is running")
    app.mainloop()
    #print(app.data_from_annotation)  
    if app.web_proc != None:
        app.web_proc.join()
    print("App is closed")
    