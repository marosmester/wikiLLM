import webbrowser
import tkinter as tk
import ttkbootstrap as tb
from PIL import Image, ImageTk
from ttkbootstrap.scrolled import ScrolledText
from tkinter.scrolledtext import ScrolledText 
import numpy as np
import cv2
import datetime
import os
import webview
import multiprocessing
import json
import copy


def multiProcessWeb(link):
    web = webview.create_window('Simple browser', link, on_top=True, x=-10, y=-2, width=650, height=840)
    webview.start()
    
def imread_unicode(path, flags=cv2.IMREAD_COLOR):
    # Read the file as a numpy array of bytes
    data = np.fromfile(path, dtype=np.uint8)
    # Decode the image from the byte array
    return cv2.imdecode(data, flags)


class AnnotationTool(tb.Window):
    def __init__(self, title="Annotation Tool", themename="litera", iconphoto='', size=None, position=None, minsize=None, maxsize=None, resizable=None, hdpi=True, scaling=None, transient=None, overrideredirect=False, alpha=1):
        super().__init__(title, themename, iconphoto, size, position, minsize, maxsize, resizable, hdpi, scaling, transient, overrideredirect, alpha)

        # Set the window size
        self.state("zoomed")
        
        # Set styles
        self.caption_font = ("Helvetica", 30, "bold")
        self.info_font = ("Helvetica", 16)
        
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
        
        # Class attributes initialization
        self.IMAGE_NEXT = ImageTk.PhotoImage(file = 'nextRecord.png')
        self.IMAGE_PREVIOUS = ImageTk.PhotoImage(file='previousRecord.png')
        self.image = None
        self.caption = None
        self.name = None
        self.birth_day = None
        self.birth_month = None
        self.birth_year = None
        self.link = None
        self.scaling_factor = None
        self.pixel_position = (None, None)
        self.person_index = 0
        self.person_sub_index = 0
        self.web_proc = None
        self.data_from_annotation = None
        self.impossible_to_fully_annotate_var = tk.IntVar(value=0)
                
        # Create a frame
        self.frames["Image"] = tb.Frame(self, padding=10)
        self.frames["Caption"] = tb.Labelframe(self, text="Image caption", padding=10)
        self.frames["Person_info_frame"]["MAIN"] = tb.Frame(self, padding=10)
        #self.frames["Person_info_frame"]["Name"] = tb.Labelframe(self.frames["Person_info_frame"]["MAIN"], text="Name", padding=10)
        self.frames["Person_info_frame"]["Birth"] = tb.Labelframe(self.frames["Person_info_frame"]["MAIN"], text="Birth Date", padding=10)
        self.frames["Person_info_frame"]["Wiki_link"] = tb.Labelframe(self.frames["Person_info_frame"]["MAIN"], text="Link to Wikipedia website", padding=10)
        self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"] = tb.Frame(self, padding=10)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"] = tb.Labelframe(self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"], text="Estimated year interval of image creation", padding=10)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"] = tb.Labelframe(self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"], text="Pixel position of the person", padding=10)
        self.frames["Control_panel"] = tb.Labelframe(self, text="Control Panel", padding=10)
        self.frames["Pos_to_annote"] = tb.Frame(self, padding=10)
        self.frames["Annotation_fail"] = tb.LabelFrame(self, text="Annotation shortcomings", padding=10)
        
        # Create a label
        self.labels["Image"] = tb.Label(self.frames["Image"])
        self.labels["Caption"] = tb.Label(self.frames["Caption"], font=self.caption_font)
        self.labels["Person_info_frame"]["Name"] = tb.Label(self, font=self.caption_font)
        #self.labels["Person_info_frame"]["Birth"] = tb.Label(self.frames["Person_info_frame"]["Birth"], font=self.info_font)
        self.labels["Wiki_link"] = tb.Label(self.frames["Person_info_frame"]["Wiki_link"], text="Link to Wikipedia page", foreground="blue", cursor="hand2", font=self.info_font)
        self.labels["Image_creation_frame_plus_pixel_pos"][";"] = tb.Label(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], text=";", font=self.info_font)
        self.labels["Image_creation_frame_plus_pixel_pos"]["("] = tb.Label(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], text="(", font=self.info_font)
        self.labels["Image_creation_frame_plus_pixel_pos"][")"] = tb.Label(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], text=")", font=self.info_font)
        self.labels["Image_creation_frame_plus_pixel_pos"]["px"] = tb.Label(self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"], text="Click on the image", font=self.info_font, width=15)
        self.labels["Control_panel"]["/"] = tb.Label(self.frames["Control_panel"], font=self.info_font)
        self.labels["Pos_to_annote"] = tb.Label(self.frames["Pos_to_annote"], text="Impossible to fully annotate?", font=self.info_font, width=15)
        
        # Create a text widget
        self.texts["Caption"] = ScrolledText(self.frames["Caption"], font=self.info_font, height = 2, width=30, wrap= "word")
        self.texts["Pos_to_annote"] = tb.ScrolledText(self.frames["Annotation_fail"], font=self.info_font, height=4, width=30, wrap="word")
        
        # Create an entry widget
        #self.entries["Person_info_frame"]["Name"] = tb.Entry(self.frames["Person_info_frame"]["Name"], font=self.info_font)
        self.entries["Person_info_frame"]["Birth"] = tb.Entry(self.frames["Person_info_frame"]["Birth"], font=self.info_font, justify="center")
        self.entries["Control_panel"]["LEFT"] = tb.Entry(self.frames["Control_panel"], font=self.info_font, width=2, justify="center")
        self.entries["Control_panel"]["RIGHT"] = tb.Entry(self.frames["Control_panel"], font=self.info_font, width=2, justify="center")
        
        #Create a combo box widget
        self.comboboxes["Person_info_frame"]["Birth"]["Day"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values=[str(i) for i in range(1,32)], width=2, justify="right")
        self.comboboxes["Person_info_frame"]["Birth"]["Month"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], width=10, justify="right")
        self.comboboxes["Person_info_frame"]["Birth"]["Year"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4, justify="right")
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"] = tb.Combobox(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4, justify="right")
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"] = tb.Combobox(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4, justify="right")
        
        #Create a button widget
        self.buttons["Next"] = tb.Button(self.frames["Control_panel"], image = self.IMAGE_NEXT, command = self.nextRecord , padding=10, width=100, takefocus=False)
        self.buttons["Previous"] = tb.Button(self.frames["Control_panel"], image = self.IMAGE_PREVIOUS, command= self.previousRecord, padding=10, width=100, takefocus=False)
        
        #Create a checkbutton widget
        self.checkbuttons["Pos_to_annote"] = tb.Checkbutton(self.frames["Pos_to_annote"], width=3, bootstyle="round-toggle", command=self.impossToFullyAnnotateCallback, variable=self.impossible_to_fully_annotate_var)
        
        #Load database
        with open("data.json", "r") as file:
            self.data = json.load(file)
        
        self.catRelatedImages()
        
        #Create a menu widget
        self.menus["Next_or_prev"] = tb.Menu(self)
        self.defaultScreenBuild()
    
    def impossToFullyAnnotateCallback(self) -> None:
        """
        Displays the next record in the database.
        Returns:
            None
        """
        if(self.checkbuttons["Pos_to_annote"].instate(["selected"])):
            self.texts["Pos_to_annote"].config(state="normal")
        else:
            self.texts["Pos_to_annote"].config(state="disabled")
    
    def catRelatedImages(self) -> None:
        """
        Concatenates images of the same person.
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
        Reads a caption from a file and assigns it to the instance variable `self.caption`.
        Args:
            captionID (int, optional): The ID of the caption to read. Defaults to 1.
        Returns:
            None
        """
        if self.data[self.person_index][self.person_sub_index]["caption"] == None:
            self.caption = ""
        else:
            self.caption = self.data[self.person_index][self.person_sub_index]["caption"]
        
        self.texts["Caption"].config(state="normal")
        self.texts["Caption"].delete("1.0", "end")
        self.texts["Caption"].insert("1.0", self.caption)
        self.texts["Caption"].config(state="disabled")
    
    def readImage(self) -> None:
        """
        Reads an image, resizes it to fit the frame, and converts it for display in a Tkinter widget.
        Args:
            imageID (int, optional): The ID of the image to read. Defaults to 1.
        Returns:
            None
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
        for i in range(len(self.data[self.person_index][self.person_sub_index]["bbox_info"])):
            bbox = self.data[self.person_index][self.person_sub_index]["bbox_info"][i]
            cv2.rectangle(resized_img, (int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)),
                          (int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)), (0, 255, 0), 3)
            
            
        # Step 3: Convert the image from BGR to RGB
        resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

        # Step 4: Convert the NumPy array to a PIL Image
        pil_img = Image.fromarray(resized_img)

        # Step 5: Convert the PIL Image to a Tkinter PhotoImage
        self.image = ImageTk.PhotoImage(pil_img)
        self.labels["Image"].config(image=self.image)
        
        
    def readPersonInfo(self) -> None:
        """
        Reads a person's information from a file and assigns it to the instance variables `self.name` and `self.birth`.
        Args:
            personID (int, optional): The ID of the person to read. Defaults to 1.
        Returns:
            None
        """
        self.parsed_path = self.data[self.person_index][self.person_sub_index]["path"].split("/")
        
        self.name = self.parsed_path[2].replace("_", " ")
        self.labels["Person_info_frame"]["Name"].config(text = self.name)
        
        self.birth_day = 7
        self.comboboxes["Person_info_frame"]["Birth"]["Day"].set(str(self.birth_day))
        
        self.birth_month = "September"
        self.comboboxes["Person_info_frame"]["Birth"]["Month"].set(self.birth_month)
        
        self.birth_year = 1944
        self.comboboxes["Person_info_frame"]["Birth"]["Year"].set(str(self.birth_year))
    
    def readWikiLink(self, personID = 1) -> None:
        """
        Reads a person's Wikipedia link from a file and returns it.
        Args:
            personID (int, optional): The ID of the person to read. Defaults to 1.
        Returns:
            str: The Wikipedia link.
        """
        with(open(f"wiki/fig{personID}.txt", "r", encoding="UTF-8")) as file:
            self.link = file.readline()
        
    
    def openWiki(self, event, link: str) -> None:
        """
        Opens a Wikipedia page in the default web browser.
        Args:
            event (tk.Event): The event object.
        Returns:
            None
        """
        
        self.web_proc = multiprocessing.Process(target=multiProcessWeb, args=(link,))
        self.web_proc.start()
        
        
    def printPixelPosition(self, event) -> None:
        """
        Prints the pixel position of the mouse click on the image.
        Args:
            event (tk.Event): The event object.
        Returns:
            None
        """
        x, y = event.x, event.y
        self.pixel_position = (int(x/self.scaling_factor), int(y/self.scaling_factor))
        img = imread_unicode(self.data[self.person_index][self.person_sub_index]["path"])
        h, w = img.shape[:2]
        resized_img = cv2.resize(img, (int(w*self.scaling_factor), int(h*self.scaling_factor)), interpolation=cv2.INTER_AREA)
        
        for i in range(len(self.data[self.person_index][self.person_sub_index]["bbox_info"])):
            bbox = self.data[self.person_index][self.person_sub_index]["bbox_info"][i]
            cv2.rectangle(resized_img, (int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)),
                          (int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)), (0, 255, 0), 3)
            if(self.pixel_position[0] >= bbox[0] and self.pixel_position[0] <= bbox[4] and 
               self.pixel_position[1] >= bbox[1] and self.pixel_position[1] <= bbox[5]):
               overlay = resized_img.copy()
               cv2.rectangle(overlay, (int(bbox[0]*self.scaling_factor), int(bbox[1]*self.scaling_factor)),
                             (int(bbox[4]*self.scaling_factor), int(bbox[5]*self.scaling_factor)), (0, 255, 0), thickness=-1)
               cv2.addWeighted(overlay, 0.4, resized_img, 0.6, 0, resized_img)
               
        resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(resized_img)
        self.image = ImageTk.PhotoImage(pil_img)
        self.labels["Image"].config(image=self.image)
                                          
        self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text=f"Pixel coordinates (x,y) are: ({x}, {y})")
     
    def openPopup(self, reference_errors: list, error_vals: list) -> None:
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
        Copies the estimated year of image creation to the right combobox.
        Returns:
            None
        """
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].set(self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].get())
    
    def getDataFromAnnotation(self) -> None:
        """
        Gets the data from the annotation and saves it to a file.
        Returns:
            None
        """
        if self.data_from_annotation == None:
            self.data_from_annotation = [[] for i in range(len(self.data))]
        
        birth_day = self.comboboxes["Person_info_frame"]["Birth"]["Day"].get()
        birth_month = self.comboboxes["Person_info_frame"]["Birth"]["Month"].get()
        birth_year = self.comboboxes["Person_info_frame"]["Birth"]["Year"].get()
        estimated_year_creation_left = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].get()
        estimated_year_creation_right = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].get()
        impossible_to_annote = self.checkbuttons["Pos_to_annote"].instate(["selected"])
        anootation_shortcommings = self.texts["Pos_to_annote"].get("1.0", "end")
        pixel_position = self.pixel_position
        
        if len(self.data_from_annotation[self.person_index]) > self.person_sub_index:
            self.data_from_annotation[self.person_index][self.person_sub_index] = {"birth_day": birth_day,
                                                                                  "birth_month": birth_month,
                                                                                  "birth_year": birth_year,
                                                                                  "estimated_year_creation_left": estimated_year_creation_left,
                                                                                  "estimated_year_creation_right": estimated_year_creation_right,
                                                                                  "impossible_to_annote": impossible_to_annote,
                                                                                  "annotation_shortcommings": anootation_shortcommings,
                                                                                  "pixel_position": pixel_position}
        else:
            self.data_from_annotation[self.person_index].append({"birth_day": birth_day,
                                                                 "birth_month": birth_month,
                                                                 "birth_year": birth_year,
                                                                 "estimated_year_creation_left": estimated_year_creation_left,
                                                                 "estimated_year_creation_right": estimated_year_creation_right,
                                                                 "impossible_to_annote": impossible_to_annote,
                                                                 "annotation_shortcommings": anootation_shortcommings,
                                                                 "pixel_position": pixel_position})
        
        print(self.data_from_annotation[self.person_index])
    
    def removeDataFromAnnotationWidgets(self) -> None:
        """
        Removes the data from the annotation widgets.
        Returns:
            None
        """
        if self.person_sub_index == 0:
            self.comboboxes["Person_info_frame"]["Birth"]["Day"].set("")
            self.comboboxes["Person_info_frame"]["Birth"]["Month"].set("")
            self.comboboxes["Person_info_frame"]["Birth"]["Year"].set("")
            self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].set("")
            self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].set("")
            self.impossible_to_fully_annotate_var.set(0)
            self.texts["Pos_to_annote"].config(state="normal")
            self.texts["Pos_to_annote"].delete("1.0", "end")
            self.texts["Pos_to_annote"].config(state="disabled")
            self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="Click on the image")
            self.pixel_position = (None, None)
        else:
            self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].set("")
            self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].set("")
            self.impossible_to_fully_annotate_var.set(0)
            self.texts["Pos_to_annote"].config(state="normal")
            self.texts["Pos_to_annote"].delete("1.0", "end")
            self.texts["Pos_to_annote"].config(state="disabled")
            self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text="Click on the image")
            self.pixel_position = (None, None)
    
    def fillDataToAnnotationWidgets(self) -> None:
        """
        Fills the data to the annotation widgets.
        Returns:
            None
        """
        birth_day = self.data_from_annotation[self.person_index][self.person_sub_index]["birth_day"]
        birth_month = self.data_from_annotation[self.person_index][self.person_sub_index]["birth_month"]
        birth_year = self.data_from_annotation[self.person_index][self.person_sub_index]["birth_year"]
        estimated_year_creation_left = self.data_from_annotation[self.person_index][self.person_sub_index]["estimated_year_creation_left"]
        estimated_year_creation_right = self.data_from_annotation[self.person_index][self.person_sub_index]["estimated_year_creation_right"]
        impossible_to_annote = self.data_from_annotation[self.person_index][self.person_sub_index]["impossible_to_annote"]
        annotation_shortcommings = self.data_from_annotation[self.person_index][self.person_sub_index]["annotation_shortcommings"]
        self.pixel_position = self.data_from_annotation[self.person_index][self.person_sub_index]["pixel_position"]
        
        pixel_position_resc = (int(self.scaling_factor*self.pixel_position[0]), int(self.scaling_factor*self.pixel_position[1]))
        
        self.comboboxes["Person_info_frame"]["Birth"]["Day"].set(birth_day)
        self.comboboxes["Person_info_frame"]["Birth"]["Month"].set(birth_month)
        self.comboboxes["Person_info_frame"]["Birth"]["Year"].set(birth_year)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].set(estimated_year_creation_left)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].set(estimated_year_creation_right)
        self.impossible_to_fully_annotate_var.set(impossible_to_annote)
        self.texts["Pos_to_annote"].config(state="normal")
        self.texts["Pos_to_annote"].delete("1.0", "end")
        self.texts["Pos_to_annote"].insert("1.0", annotation_shortcommings)
        self.texts["Pos_to_annote"].config(state="disabled")
        self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text=f"Pixel coordinates (x,y) are: ({pixel_position_resc[0]}, {pixel_position_resc[1]})")
        
    def nextRecord(self) -> None:
        """
        Displays the next record in the database.
        Returns:
            None
        """
        list_of_errors = ["Birth day is not filled or is not an integer in the range 1-31!",
                          "Birth month is not filled or is not an integer in the range 1-12 or its name is written incorrectly!",
                          "Birth year is not filled or is not an integer lower than the current year!",
                          "Estimated year of image creation (left boundary) is not filled or is not an integer lower than the current year!",
                          "Estimated year of image creation (right boundary) is not filled or is not an integer lower than the current year!",
                          "Estimated year of image creation (right boundary) is lower than its (left boundary)!",
                          "Bounding box was not picked!"]
        
        list_or_errors_vals = [False, False, False, False, False, False, False]
        list_of_month_names = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        
        birth_day = self.comboboxes["Person_info_frame"]["Birth"]["Day"].get()
        birth_month = self.comboboxes["Person_info_frame"]["Birth"]["Month"].get()
        birth_year = self.comboboxes["Person_info_frame"]["Birth"]["Year"].get()
        estimated_year_creation_left = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].get()
        estimated_year_creation_right = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].get()
        pixel_position = self.pixel_position
        
        if not birth_day.isdigit() or int(birth_day) not in range(1,32):
            list_or_errors_vals[0] = True
        if not birth_month.isdigit() and birth_month.lower() not in list_of_month_names:
            list_or_errors_vals[1] = True
        if birth_month.isdigit() and int(birth_month) not in range(1,13):
            list_or_errors_vals[1] = True
        if not birth_year.isdigit() or int(birth_year) not in range(datetime.date.today().year + 1):
            list_or_errors_vals[2] = True
        if estimated_year_creation_left == "" or not estimated_year_creation_left.isdigit() or int(estimated_year_creation_left) not in range(datetime.date.today().year + 1):
            list_or_errors_vals[3] = True
        if estimated_year_creation_right == "" or not estimated_year_creation_right.isdigit() or int(estimated_year_creation_right) not in range(datetime.date.today().year + 1):
            list_or_errors_vals[4] = True
        if estimated_year_creation_left.isdigit() and estimated_year_creation_right.isdigit() and int(estimated_year_creation_right) < int(estimated_year_creation_left):
            list_or_errors_vals[5] = True
        if pixel_position == (None, None):
            list_or_errors_vals[6] = True
        
        if any(list_or_errors_vals) and not self.checkbuttons["Pos_to_annote"].instate(["selected"]):
            self.openPopup(list_of_errors, list_or_errors_vals)
        else:
            self.getDataFromAnnotation()
            
            if(self.person_sub_index + 1 == len(self.data[self.person_index])):
                self.person_index += 1
                self.person_sub_index = 0
            else:
                self.person_sub_index += 1
            
            self.entries["Control_panel"]["LEFT"].config(state="normal")
            self.entries["Control_panel"]["LEFT"].delete(0, "end")
            self.entries["Control_panel"]["LEFT"].insert(0, str(self.person_sub_index + 1))
            self.entries["Control_panel"]["LEFT"].config(state="readonly")
            
            self.entries["Control_panel"]["RIGHT"].config(state="normal")
            self.entries["Control_panel"]["RIGHT"].delete(0, "end")
            self.entries["Control_panel"]["RIGHT"].insert(0, str(len(self.data[self.person_index])))
            self.entries["Control_panel"]["RIGHT"].config(state="readonly")
            
            if self.data_from_annotation[self.person_index] != []:
                self.fillDataToAnnotationWidgets()
            else:
                self.removeDataFromAnnotationWidgets()
                
            self.readCaption()
            self.readImage()
            self.readPersonInfo()
            self.readWikiLink()
            
            if self.web_proc != None:
                self.web_proc.terminate()
                self.web_proc.join()
    
    def previousRecord(self) -> None:
        """
        Displays the previous record in the database.
        Returns:
            None
        """
        """
        list_of_errors = ["Birth day is not filled!",
                          "Birth day is not integer in the range 1-31!",
                          "Birth month is not filled!",
                          "Birth month is not integer in the range 1-12 or its name is written incorrectly!",
                          "Birth year is not filled!",
                          "Birth year is not integer lower than the current year!",
                          "Estimated year of image creation (left boundary) is not filled!",
                          "Estimated year of image creation (left boundary) is not integer lower than the current year!",
                          "Estimated year of image creation (right boundary) is not filled!",
                          "Estimated year of image creation (right boundary) is not integer lower than the current year!",
                          "Pixel position is not filled!"]
        
        list_or_errors_vals = [False, False, False, False, False, False, False, False, False, False, False]
        list_of_month_names = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        
        birth_day = self.comboboxes["Person_info_frame"]["Birth"]["Day"].get()
        birth_month = self.comboboxes["Person_info_frame"]["Birth"]["Month"].get()
        birth_year = self.comboboxes["Person_info_frame"]["Birth"]["Year"].get()
        estimated_year_creation_left = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].get()
        estimated_year_creation_right = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].get()
        pixel_position = self.pixel_position
        
        if birth_day == "":
            list_or_errors_vals[0] = True
        if not birth_day.isdigit() or int(birth_day) not in range(1,32):
            list_or_errors_vals[1] = True
        if birth_month == "":
            list_or_errors_vals[2] = True
        if not birth_month.isdigit() and birth_month.lower() not in list_of_month_names:
            list_or_errors_vals[3] = True
        if birth_month.isdigit() and int(birth_month) not in range(1,13):
            list_or_errors_vals[3] = True
        if birth_year == "":
            list_or_errors_vals[4] = True
        if not birth_year.isdigit() or int(birth_year) not in range(datetime.date.today().year + 1):
            list_or_errors_vals[5] = True
        if estimated_year_creation_left == "":
            list_or_errors_vals[6] = True
        if not estimated_year_creation_left.isdigit() or int(estimated_year_creation_left) not in range(datetime.date.today().year + 1):
            list_or_errors_vals[7] = True
        if estimated_year_creation_right == "":
            list_or_errors_vals[8] = True
        if not estimated_year_creation_right.isdigit() or int(estimated_year_creation_right) not in range(datetime.date.today().year + 1):
            list_or_errors_vals[9] = True
        if pixel_position == (None, None):
            list_or_errors_vals[10] = True
        """
        """
        if any(list_or_errors_vals):
            self.openPopup(list_of_errors, list_or_errors_vals)
        else:
        """
        
        if(self.person_sub_index == 0):
            if(self.person_index != 0):
                self.person_index -= 1
                self.person_sub_index = len(self.data[self.person_index]) - 1
                print("in")
        else:
            self.person_sub_index -= 1
        
        self.entries["Control_panel"]["LEFT"].config(state="normal")
        self.entries["Control_panel"]["LEFT"].delete(0, "end")
        self.entries["Control_panel"]["LEFT"].insert(0, str(self.person_sub_index + 1))
        self.entries["Control_panel"]["LEFT"].config(state="readonly")
        
        self.entries["Control_panel"]["RIGHT"].config(state="normal")
        self.entries["Control_panel"]["RIGHT"].delete(0, "end")
        self.entries["Control_panel"]["RIGHT"].insert(0, str(len(self.data[self.person_index])))
        self.entries["Control_panel"]["RIGHT"].config(state="readonly")
        
        self.fillDataToAnnotationWidgets()
        self.readCaption()
        self.readImage()
        self.readPersonInfo()
        self.readWikiLink()
        
        if self.web_proc != None:
            self.web_proc.terminate()
            self.web_proc.join()
            
    
    def defaultScreenBuild(self):
        
        # Set the layout
        self.update()
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, minsize = int(self.winfo_width()/3), weight=1)
        self.grid_columnconfigure(1, minsize = int(self.winfo_width()/2), weight=1)
        
        # Place the lefthand frames
        self.frames["Image"].grid(row=0, column=0, rowspan = 5, sticky="nsew", padx=10, pady=40)
        
        #Place the righthand frames
        self.frames["Caption"].grid(row=5, column=0, sticky="ew", padx=27, pady=20, ipady=10)
        self.frames["Person_info_frame"]["MAIN"].grid(row=1, column=1, sticky="ew", padx=10, pady=20)
        self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"].grid(row=2, column=1, sticky="ew", padx=10, pady=20)
        self.frames["Control_panel"].grid(row=5, column=1, sticky="ew", padx=20, pady=20, ipady=11)
        self.frames["Pos_to_annote"].grid(row=3, column=1, sticky="ew", padx=20, pady=20, ipady=10)
        self.frames["Annotation_fail"].grid(row=4, column=1, sticky="ew", padx=20, pady=20, ipady=10)
        
        
        # Update and place the image and caption
        self.readCaption()
        self.readImage()
        self.readPersonInfo()
        
        #self.labels["Image"].config(image=self.image)
        self.labels["Image"].place(relx=0.5, rely=0.5, anchor="center")
        self.labels["Image"].bind("<Button-1>", self.printPixelPosition)
        
        self.texts["Caption"].insert("1.0", self.caption)
        self.texts["Caption"].pack(fill="both", expand=True)
        self.texts["Caption"].config(state="disabled")
        
        #self.labels["Person_info_frame"]["Name"].config(text = self.name)
        self.labels["Person_info_frame"]["Name"].grid(row=0, column=1, sticky="ns", padx=10)
        
        # Place the person info frames
        
        self.frames["Person_info_frame"]["MAIN"].grid_rowconfigure(0, weight=1)
        self.frames["Person_info_frame"]["MAIN"].grid_columnconfigure(0, weight=5)
        self.frames["Person_info_frame"]["MAIN"].grid_columnconfigure(1, weight=1)
        
        #self.frames["Person_info_frame"]["Name"].grid(row=0, column=0, sticky="ew", padx=10)
        self.frames["Person_info_frame"]["Birth"].grid(row=0, column=1, sticky="ew", padx=10)
        
        # Update and place the person info entries
        
        #self.frames["Person_info_frame"]["Name"].grid_rowconfigure(0, weight=1)
        #self.frames["Person_info_frame"]["Name"].grid_columnconfigure(0, weight=1)
        
        #self.entries["Person_info_frame"]["Name"].grid(row=0, column=0, sticky="ew")
        
        
        self.comboboxes["Person_info_frame"]["Birth"]["Day"].grid(row=0, column=0, padx=10)
        self.comboboxes["Person_info_frame"]["Birth"]["Month"].grid(row=0, column=1, padx=10)
        self.comboboxes["Person_info_frame"]["Birth"]["Year"].grid(row=0, column=2, padx=10)
        
        # Place and update the image creation frame and pixel position frame
        self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"].grid_rowconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"].grid_columnconfigure(0, weight=5)
        self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"].grid_columnconfigure(1, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid(row=0, column=1, sticky="ew", padx=10)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"].grid(row=0, column=0, sticky="nsew", padx=0)
        
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_rowconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(1, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(2, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(3, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(4, weight=1)
        
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"].grid_rowconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"].grid_columnconfigure(0, weight=1)
        
        
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].grid(row=0, column=1, padx=10)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"].bind("<<ComboboxSelected>>", self.estimatedYearCreationCopy)
        self.labels["Image_creation_frame_plus_pixel_pos"][";"].grid(row=0, column=2, padx=22)
        self.labels["Image_creation_frame_plus_pixel_pos"]["("].grid(row=0, column=0, padx=21)
        self.labels["Image_creation_frame_plus_pixel_pos"][")"].grid(row=0, column=4, padx=21)
        
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"].grid(row=0, column=3, padx=10)
        #self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Uncertainty"].set("0")
        self.labels["Image_creation_frame_plus_pixel_pos"]["px"].grid(row=0, column=0, sticky="ew", padx=10)
        
        
        # Update and place Wikipedia link
        self.readWikiLink()
        
        self.frames["Person_info_frame"]["Wiki_link"].grid_rowconfigure(0, weight=1)
        self.frames["Person_info_frame"]["Wiki_link"].grid_columnconfigure(0, weight=1)
        
        
        self.frames["Person_info_frame"]["Wiki_link"].grid(row=0, column=0, sticky="nsew")
        self.labels["Wiki_link"].config(text = "Open Wikipedia page")
        self.labels["Wiki_link"].grid(row=0, column=0, sticky="ew")
        self.labels["Wiki_link"].bind("<Button-1>", lambda k: self.openWiki(k,self.link))
        
        # Update and place the control panel widgets
        
        self.frames["Control_panel"].grid_rowconfigure(0, weight=1)
        self.frames["Control_panel"].grid_columnconfigure(0, weight=10)
        self.frames["Control_panel"].grid_columnconfigure(1, weight=1)
        self.frames["Control_panel"].grid_columnconfigure(2, weight=1)
        self.frames["Control_panel"].grid_columnconfigure(3, weight=1)
        self.frames["Control_panel"].grid_columnconfigure(4, weight=10)
        
        self.buttons["Previous"].grid(row=0, column=0, padx=10)
        self.buttons["Next"].grid(row=0, column=4, padx=10)
        
        self.labels["Control_panel"]["/"].config(text="/")
        self.labels["Control_panel"]["/"].grid(row=0, column=2, padx=0)
        
        self.entries["Control_panel"]["LEFT"].grid(row=0, column=1, padx=0, sticky="e")
        self.entries["Control_panel"]["LEFT"].insert(0, str(self.person_sub_index + 1))
        self.entries["Control_panel"]["LEFT"].state(["readonly"])
        self.entries["Control_panel"]["RIGHT"].grid(row=0, column=3, padx=0, sticky="w")
        self.entries["Control_panel"]["RIGHT"].insert(0, str(len(self.data[self.person_index])))
        self.entries["Control_panel"]["RIGHT"].state(["readonly"])
        
        # Update and place possible to fully annotate widgets
        
        self.frames["Pos_to_annote"].grid_rowconfigure(0, weight=1)
        self.frames["Pos_to_annote"].grid_columnconfigure(0, weight=1)
        self.frames["Pos_to_annote"].grid_columnconfigure(1, weight=1)
        
        self.labels["Pos_to_annote"].grid(row=0, column=0, padx=10, ipadx = 60, sticky="nse")
        self.checkbuttons["Pos_to_annote"].grid(row=0, column=1, padx=10, sticky="w", ipadx=10)
        
        # Update and place the annotation shortcomings widgets
        self.frames["Annotation_fail"].grid_rowconfigure(0, weight=1)
        self.frames["Annotation_fail"].grid_columnconfigure(0, weight=1)
        
        self.texts["Pos_to_annote"].grid(row=0, column=0, padx=10, sticky="nsew")
        self.texts["Pos_to_annote"].config(state="disabled")
        
        

        

if __name__ == "__main__":
    multiprocessing.freeze_support() # Required for Windows
    theme_lightness = 0
    
    if not theme_lightness:
        app = AnnotationTool(themename="cosmo")
    else:
        app = AnnotationTool(themename="darkly")
        
    print("App is running")
    app.mainloop()
    app.web_proc.join()
    print("App is closed")
    