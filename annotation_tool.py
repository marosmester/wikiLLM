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


def multiProcessWeb(link):
    web = webview.create_window('Simple browser', link, on_top=True, x=-10, y=-2, width=650, height=840)
    webview.start()


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
        self.labels["Pos_to_annote"] = tb.Label(self.frames["Pos_to_annote"], text="Possible to fully annotate?", font=self.info_font, width=15)
        
        # Create a text widget
        self.texts["Caption"] = ScrolledText(self.frames["Caption"], font=self.info_font, height = 2, width=30, wrap= "word")
        self.texts["Pos_to_annote"] = tb.ScrolledText(self.frames["Annotation_fail"], font=self.info_font, height=4, width=30, wrap="word")
        
        # Create an entry widget
        #self.entries["Person_info_frame"]["Name"] = tb.Entry(self.frames["Person_info_frame"]["Name"], font=self.info_font)
        self.entries["Person_info_frame"]["Birth"] = tb.Entry(self.frames["Person_info_frame"]["Birth"], font=self.info_font)
        self.entries["Control_panel"]["LEFT"] = tb.Entry(self.frames["Control_panel"], font=self.info_font, width=2)
        self.entries["Control_panel"]["RIGHT"] = tb.Entry(self.frames["Control_panel"], font=self.info_font, width=2)
        
        #Create a combo box widget
        self.comboboxes["Person_info_frame"]["Birth"]["Day"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values=[str(i) for i in range(1,32)], width=2)
        self.comboboxes["Person_info_frame"]["Birth"]["Month"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], width=10)
        self.comboboxes["Person_info_frame"]["Birth"]["Year"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_left"] = tb.Combobox(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year_right"] = tb.Combobox(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4)
        
        #Create a button widget
        self.buttons["Next"] = tb.Button(self.frames["Control_panel"], image = self.IMAGE_NEXT, command = self.nextRecord , padding=10, width=100, takefocus=False)
        self.buttons["Previous"] = tb.Button(self.frames["Control_panel"], image = self.IMAGE_PREVIOUS, command= self.previousRecord, padding=10, width=100, takefocus=False)
        
        #Create a checkbutton widget
        self.checkbuttons["Pos_to_annote"] = tb.Checkbutton(self.frames["Pos_to_annote"], width=3, bootstyle="round-toggle")
        
        #Load database
        with open("data.json", "r") as file:
            self.data = json.load(file)
        
        self.catRelatedImages()
        
        #Create a menu widget
        self.menus["Next_or_prev"] = tb.Menu(self)
        self.defaultScreenBuild()
        
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
        
    def readCaption(self, captionID = 1) -> None:
        """
        Reads a caption from a file and assigns it to the instance variable `self.caption`.
        Args:
            captionID (int, optional): The ID of the caption to read. Defaults to 1.
        Returns:
            None
        """
        with(open(f"captions/fig{captionID}.txt", "r")) as file:
            caption = file.readline() + "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
        
        self.caption = caption
    
    def faceDetection(self, img: np.ndarray) -> np.ndarray:
        """
        Detects faces in an image using the Haar cascade classifier.
        Args:
            img (np.ndarray): The image to process.
        Returns:
            Any: The processed image.
        """
        # Load the Haar cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Draw rectangles around the detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
        
        return img
    
    def readImage(self, imageID = 1) -> None:
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
        img = cv2.imread(f"figs/fig{imageID}.jpg")
        h, w = img.shape[:2]
        
        resizing_factor = min(self.image_frame_size[0]/w, self.image_frame_size[1]/h)
        self.scaling_factor = resizing_factor
        resized_img = cv2.resize(img, (int(w*resizing_factor), int(h*resizing_factor)), interpolation=cv2.INTER_AREA)
        
        #Step 3: Detect faces in the image
        resized_img = self.faceDetection(resized_img)
        
        # Step 3: Convert the image from BGR to RGB
        resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

        # Step 4: Convert the NumPy array to a PIL Image
        pil_img = Image.fromarray(resized_img)

        # Step 5: Convert the PIL Image to a Tkinter PhotoImage
        self.image = ImageTk.PhotoImage(pil_img)
        
    def readPersonInfo(self, personID = 1) -> None:
        """
        Reads a person's information from a file and assigns it to the instance variables `self.name` and `self.birth`.
        Args:
            personID (int, optional): The ID of the person to read. Defaults to 1.
        Returns:
            None
        """    
        self.name = "Miloš Zeman"
        self.birth_day = 7
        self.birth_month = "September"
        self.birth_year = 1944
    
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
        self.labels["Image_creation_frame_plus_pixel_pos"]["px"].config(text=f"Pixel coordinates (x,y) are: ({x}, {y})")
     
    def openPopup(self, reference_errors: list, error_vals: list) -> None:
        # Create a new popup window (Toplevel)
        
        popup = tb.Toplevel(self)
        popup.title("Error")
        popup_width = 600
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
        
    
    def nextRecord(self) -> None:
        """
        Displays the next record in the database.
        Returns:
            None
        """
        list_of_errors = ["Name is not filled!",
                          "Birth day is not filled!",
                          "Birth day is not integer in the range 1-31!",
                          "Birth month is not filled!",
                          "Birth month is not integer in the range 1-12 or its name is written incorrectly!",
                          "Birth year is not filled!",
                          f"Birth year is not integer lower than the current year!",
                          "Estimated year of image creation is not filled!",
                          "Estimated year of image creation is not integer lower than the current year!",
                          "Estimated year of image creation uncertainty is not filled!",
                          "Estimated year of image creation uncertainty is not integer!",
                          "Pixel position is not filled!"]
        
        list_or_errors_vals = [False, False, False, False, False, False, False, False, False, False, False, False]
        list_of_month_names = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        
        name = self.entries["Person_info_frame"]["Name"].get()
        birth_day = self.comboboxes["Person_info_frame"]["Birth"]["Day"].get()
        birth_month = self.comboboxes["Person_info_frame"]["Birth"]["Month"].get()
        birth_year = self.comboboxes["Person_info_frame"]["Birth"]["Year"].get()
        estimated_year_creation = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year"].get()
        estimated_year_uncertainty = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Uncertainty"].get()
        pixel_position = self.pixel_position
        
        if name == "":
            list_or_errors_vals[0] = True
        if birth_day == "":
            list_or_errors_vals[1] = True
        if not birth_day.isdigit() or int(birth_day) not in range(1,32):
            list_or_errors_vals[2] = True
        if birth_month == "":
            list_or_errors_vals[3] = True
        if not birth_month.isdigit() and birth_month.lower() not in list_of_month_names:
            list_or_errors_vals[4] = True
        if birth_month.isdigit() and int(birth_month) not in range(1,13):
            list_or_errors_vals[4] = True
        if birth_year == "":
            list_or_errors_vals[5] = True
        if not birth_year.isdigit() or int(birth_year) not in range(datetime.date.today().year + 1):
            list_or_errors_vals[6] = True
        if estimated_year_creation == "":
            list_or_errors_vals[7] = True
        if not estimated_year_creation.isdigit() or int(estimated_year_creation) not in range(datetime.date.today().year + 1):
            list_or_errors_vals[8] = True
        if estimated_year_uncertainty == "":
            list_or_errors_vals[9] = True
        if not estimated_year_uncertainty.isdigit():
            list_or_errors_vals[10] = True
        if pixel_position == (None, None):
            list_or_errors_vals[11] = True
        
        if any(list_or_errors_vals):
            self.openPopup(list_of_errors, list_or_errors_vals)
        else:
            self.web_proc.terminate()
            self.web_proc.join()
    
    def previousRecord(self) -> None:
        """
        Displays the previous record in the database.
        Returns:
            None
        """
        
        list_of_errors = ["Name is not filled!",
                          "Birth day is not filled!",
                          "Birth day is not integer in the range 1-31!",
                          "Birth month is not filled!",
                          "Birth month is not integer in the range 1-12 or its name is written incorrectly!",
                          "Birth year is not filled!",
                          f"Birth year is not integer lower than the current year!",
                          "Estimated year of image creation is not filled!",
                          "Estimated year of image creation is not integer lower than the current year!",
                          "Estimated year of image creation uncertainty is not filled!",
                          "Estimated year of image creation uncertainty is not integer!",
                          "Pixel position is not filled!"]
        
        list_or_errors_vals = [False, False, False, False, False, False, False, False, False, False, False, False]
        list_of_month_names = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        
        name = self.entries["Person_info_frame"]["Name"].get()
        birth_day = self.comboboxes["Person_info_frame"]["Birth"]["Day"].get()
        birth_month = self.comboboxes["Person_info_frame"]["Birth"]["Month"].get()
        birth_year = self.comboboxes["Person_info_frame"]["Birth"]["Year"].get()
        estimated_year_creation = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year"].get()
        estimated_year_uncertainty = self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Uncertainty"].get()
        pixel_position = self.pixel_position
        
        if name == "":
            list_or_errors_vals[0] = True
        if birth_day == "":
            list_or_errors_vals[1] = True
        if not birth_day.isdigit() or int(birth_day) not in range(1,32):
            list_or_errors_vals[2] = True
        if birth_month == "":
            list_or_errors_vals[3] = True
        if not birth_month.isdigit() and birth_month.lower() not in list_of_month_names:
            list_or_errors_vals[4] = True
        if birth_month.isdigit() and int(birth_month) not in range(1,13):
            list_or_errors_vals[4] = True
        if birth_year == "":
            list_or_errors_vals[5] = True
        if not birth_year.isdigit() or int(birth_year) not in range(datetime.date.today().year + 1):
            list_or_errors_vals[6] = True
        if estimated_year_creation == "":
            list_or_errors_vals[7] = True
        if not estimated_year_creation.isdigit() or int(estimated_year_creation) not in range(datetime.date.today().year + 1):
            list_or_errors_vals[8] = True
        if estimated_year_uncertainty == "":
            list_or_errors_vals[9] = True
        if not estimated_year_uncertainty.isdigit():
            list_or_errors_vals[10] = True
        if pixel_position == (None, None):
            list_or_errors_vals[11] = True
        
        if any(list_or_errors_vals):
            self.openPopup(list_of_errors, list_or_errors_vals)
        else:
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
        
        self.labels["Image"].config(image=self.image)
        self.labels["Image"].place(relx=0.5, rely=0.5, anchor="center")
        self.labels["Image"].bind("<Button-1>", self.printPixelPosition)
        
        self.texts["Caption"].insert("1.0", self.caption)
        self.texts["Caption"].pack(fill="both", expand=True)
        self.texts["Caption"].config(state="disabled")
        
        self.labels["Person_info_frame"]["Name"].config(text = self.name)
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
        self.entries["Control_panel"]["LEFT"].state(["readonly"])
        self.entries["Control_panel"]["RIGHT"].grid(row=0, column=3, padx=0, sticky="w")
        self.entries["Control_panel"]["RIGHT"].state(["readonly"])
        
        # Update and place possible to fully annotate widgets
        
        self.frames["Pos_to_annote"].grid_rowconfigure(0, weight=1)
        self.frames["Pos_to_annote"].grid_columnconfigure(0, weight=1)
        self.frames["Pos_to_annote"].grid_columnconfigure(1, weight=1)
        
        self.labels["Pos_to_annote"].grid(row=0, column=0, padx=10, ipadx = 50, sticky="nse")
        self.checkbuttons["Pos_to_annote"].grid(row=0, column=1, padx=10, sticky="w", ipadx=10)
        
        # Update and place the annotation shortcomings widgets
        self.frames["Annotation_fail"].grid_rowconfigure(0, weight=1)
        self.frames["Annotation_fail"].grid_columnconfigure(0, weight=1)
        
        self.texts["Pos_to_annote"].grid(row=0, column=0, padx=10, sticky="nsew")
        
        

        

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
    