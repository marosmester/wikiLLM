import webbrowser
import tkinter as tk
import ttkbootstrap as tb
from PIL import Image, ImageTk
from ttkbootstrap.scrolled import ScrolledText
import numpy as np
import cv2
import datetime

class AnnotationTool(tb.Window):
    def __init__(self, title="Annotation Tool", themename="litera", iconphoto='', size=None, position=None, minsize=None, maxsize=None, resizable=None, hdpi=True, scaling=None, transient=None, overrideredirect=False, alpha=1):
        super().__init__(title, themename, iconphoto, size, position, minsize, maxsize, resizable, hdpi, scaling, transient, overrideredirect, alpha)

        # Set the window size
        self.state("zoomed")
        
        # Set styles
        self.caption_font = ("Helvetica", 16)
        self.info_font = ("Helvetica", 16)
        
        # Widget dictionaries initialization
        self.frames = {'Person_info_frame': {},
                       'Image_creation_frame_plus_pixel_pos': {}}
        self.buttons = {'Person_info_frame': {}}
        self.labels = {'Person_info_frame': {},
                       'Image_creation_frame_plus_pixel_pos': {}}
        self.entries = {'Person_info_frame': {}}
        self.texts = {'Person_info_frame': {}}
        self.comboboxes = {'Person_info_frame': { "Birth":  {}},
                           'Image_creation_frame_plus_pixel_pos': {}}
        
        # Class attributes initialization
        self.IMAGE_NEXT = ImageTk.PhotoImage(file = 'nextRecord.png')
        self.IMAGE_PREVIOUS = ImageTk.PhotoImage(file='previousRecord.png')
        self.image = None
        self.caption = None
        self.name = None
        self.birth = None
        self.link = None
        self.scaling_factor = None
        self.pixel_position = (None, None)
                
        # Create a frame
        self.frames["Image"] = tb.Frame(self, padding=10)
        self.frames["Caption"] = tb.Labelframe(self, text="Image caption", padding=10)
        self.frames["Person_info_frame"]["MAIN"] = tb.Frame(self, padding=10)
        self.frames["Person_info_frame"]["Name"] = tb.Labelframe(self.frames["Person_info_frame"]["MAIN"], text="Name", padding=10)
        self.frames["Person_info_frame"]["Birth"] = tb.Labelframe(self.frames["Person_info_frame"]["MAIN"], text="Birth Date", padding=10)
        self.frames["Wiki_link"] = tb.Labelframe(self, text="Link to Wikipedia website", padding=10)
        self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"] = tb.Frame(self, padding=10)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"] = tb.Labelframe(self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"], text="Estimated year of image creation", padding=10)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"] = tb.Labelframe(self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"], text="Pixel position of the person", padding=10)
        
        self.frames["Control_panel"] = tb.Labelframe(self, text="Control Panel", padding=10)
        
        # Create a label
        self.labels["Image"] = tb.Label(self.frames["Image"])
        self.labels["Caption"] = tb.Label(self.frames["Caption"], font=self.caption_font)
        #self.labels["Person_info_frame"]["Name"] = tb.Label(self.frames["Person_info_frame"]["Name"], font=self.info_font)
        #self.labels["Person_info_frame"]["Birth"] = tb.Label(self.frames["Person_info_frame"]["Birth"], font=self.info_font)
        self.labels["Wiki_link"] = tb.Label(self.frames["Wiki_link"], text="Link to Wikipedia page", foreground="blue", cursor="hand2", font=self.info_font)
        self.labels["Image_creation_frame_plus_pixel_pos"]["pm"] = tb.Label(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], text="±", font=self.info_font)
        self.labels["Image_creation_frame_plus_pixel_pos"]["px"] = tb.Label(self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"], text="Click on the image", font=self.info_font, width=15)
        
        # Create a text widget
        self.texts["Caption"] = ScrolledText(self.frames["Caption"], font=self.info_font, height=5, width=30, wrap= "word", autohide = True)
        
        # Create an entry widget
        self.entries["Person_info_frame"]["Name"] = tb.Entry(self.frames["Person_info_frame"]["Name"], font=self.info_font)
        self.entries["Person_info_frame"]["Birth"] = tb.Entry(self.frames["Person_info_frame"]["Birth"], font=self.info_font)
        
        #Create a combo box widget
        self.comboboxes["Person_info_frame"]["Birth"]["Day"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values=[str(i) for i in range(1,32)], width=2)
        self.comboboxes["Person_info_frame"]["Birth"]["Month"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], width=10)
        self.comboboxes["Person_info_frame"]["Birth"]["Year"] = tb.Combobox(self.frames["Person_info_frame"]["Birth"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year"] = tb.Combobox(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], font=self.info_font, values= sorted([str(i) for i in range(1000,datetime.date.today().year + 1)], reverse=True),width=4)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Uncertainty"] = tb.Combobox(self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"], font=self.info_font, values= [str(i) for i in range(101)],width=2)
        
        #Create a button widget
        self.buttons["Next"] = tb.Button(self.frames["Control_panel"], image = self.IMAGE_NEXT, command = self.nextRecord , padding=10, width=100, takefocus=False)
        self.buttons["Previous"] = tb.Button(self.frames["Control_panel"], image = self.IMAGE_PREVIOUS, command= self.previousRecord, padding=10, width=100, takefocus=False)
        
        self.defaultScreenBuild()
        
    def readCaption(self, captionID = 1) -> None:
        """
        Reads a caption from a file and assigns it to the instance variable `self.caption`.
        Args:
            captionID (int, optional): The ID of the caption to read. Defaults to 1.
        Returns:
            None
        """
        with(open(f"captions/fig{captionID}.txt", "r")) as file:
            caption = file.readline() + "ahoj ahoj ahoj ahoj ahoj ahoj ahoj ahoj ahoj ahoj ahoj ahoj ahoj ahoj ahoj ahoj ahoj"
        
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
        with(open(f"person_info/fig{personID}.txt", "r", encoding="UTF-8")) as file:
            for i in file:
                if(i.startswith("Name")):
                    name = i.split(":")[1].strip()
                elif(i.startswith("Birth")):
                    birth = i.split(":")[1].strip()
            
        self.name = name
        self.birth = birth
    
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
        print(link)
        webbrowser.open(link)
        
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
    
    def nextRecord(self) -> None:
        """
        Displays the next record in the database.
        Returns:
            None
        """
        pass
    
    def previousRecord(self) -> None:
        """
        Displays the previous record in the database.
        Returns:
            None
        """
        pass
        

    def defaultScreenBuild(self):
        
        # Set the layout
        self.update()
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=20)
        self.grid_columnconfigure(0, minsize = int(self.winfo_width()/3), weight=1)
        self.grid_columnconfigure(1, minsize = int(self.winfo_width()/2), weight=1)
        
        # Place the lefthand frames
        self.frames["Image"].grid(row=0, column=0, rowspan = 5, sticky="nsew", padx=10, pady=40)
        
        #Place the righthand frames
        self.frames["Caption"].grid(row=0, column=1, sticky="ew", padx=27, pady=20)
        self.frames["Wiki_link"].grid(row=1, column=1, sticky="ew", padx=27, pady=10)
        self.frames["Person_info_frame"]["MAIN"].grid(row=2, column=1, sticky="ew", padx=10, pady=20)
        self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"].grid(row=3, column=1, sticky="ew", padx=10, pady=20)
        self.frames["Control_panel"].grid(row=4, column=1, sticky="ew", padx=27, pady=20, ipady=20)
        
        
        # Update and place the image and caption
        self.readCaption()
        self.readImage()
        
        self.labels["Image"].config(image=self.image)
        self.labels["Image"].place(relx=0.5, rely=0.5, anchor="center")
        self.labels["Image"].bind("<Button-1>", self.printPixelPosition)
        
        #self.labels["Caption"].config(text=self.caption)
        self.texts["Caption"].insert("1.0", self.caption)
        #self.texts["Caption"].config(
        self.texts["Caption"].pack(fill="both", expand=True)
        
        # Place the person info frames
        
        self.frames["Person_info_frame"]["MAIN"].grid_rowconfigure(0, weight=1)
        self.frames["Person_info_frame"]["MAIN"].grid_columnconfigure(0, weight=5)
        self.frames["Person_info_frame"]["MAIN"].grid_columnconfigure(1, weight=1)
        
        self.frames["Person_info_frame"]["Name"].grid(row=0, column=0, sticky="ew", padx=10)
        self.frames["Person_info_frame"]["Birth"].grid(row=0, column=1, sticky="ew", padx=10)
        
        # Update and place the person info entries
        
        self.frames["Person_info_frame"]["Name"].grid_rowconfigure(0, weight=1)
        self.frames["Person_info_frame"]["Name"].grid_columnconfigure(0, weight=1)
        
        self.entries["Person_info_frame"]["Name"].grid(row=0, column=0, sticky="ew")
        self.comboboxes["Person_info_frame"]["Birth"]["Day"].grid(row=0, column=0, padx=10)
        self.comboboxes["Person_info_frame"]["Birth"]["Month"].grid(row=0, column=1, padx=10)
        self.comboboxes["Person_info_frame"]["Birth"]["Year"].grid(row=0, column=2, padx=10)
        
        # Place and update the image creation frame and pixel position frame
        self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"].grid_rowconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"].grid_columnconfigure(0, weight=2)
        self.frames["Image_creation_frame_plus_pixel_pos"]["MAIN"].grid_columnconfigure(1, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid(row=0, column=1, sticky="ew", padx=10, ipadx=30)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"].grid(row=0, column=0, sticky="nsew", padx=10)
        
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_rowconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(1, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Image_creation_frame"].grid_columnconfigure(2, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"].grid_rowconfigure(0, weight=1)
        self.frames["Image_creation_frame_plus_pixel_pos"]["Pixel_position"].grid_columnconfigure(0, weight=1)
        
        
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Year"].grid(row=0, column=0, padx=10)
        self.labels["Image_creation_frame_plus_pixel_pos"]["pm"].grid(row=0, column=1, padx=10)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Uncertainty"].grid(row=0, column=2, padx=10)
        self.comboboxes["Image_creation_frame_plus_pixel_pos"]["Uncertainty"].set("0")
        self.labels["Image_creation_frame_plus_pixel_pos"]["px"].grid(row=0, column=0, sticky="ew", padx=10)
        
        
        # Update and place Wikipedia link
        self.readWikiLink()
        
        self.labels["Wiki_link"].config(text = self.link)
        self.labels["Wiki_link"].grid(row=0, column=0, sticky="ew")
        self.labels["Wiki_link"].bind("<Button-1>", lambda k: self.openWiki(k,self.link))
        
        # Update and place the control panel widgets
        
        self.frames["Control_panel"].grid_rowconfigure(0, weight=1)
        self.frames["Control_panel"].grid_columnconfigure(0, weight=1)
        self.frames["Control_panel"].grid_columnconfigure(1, weight=1)
        
        self.buttons["Previous"].grid(row=0, column=0, padx=10)
        self.buttons["Next"].grid(row=0, column=1, padx=10)
        
        

if __name__ == "__main__":
    
    theme_lightness = 0
    
    if not theme_lightness:
        app = AnnotationTool(themename="cosmo")
    else:
        app = AnnotationTool(themename="darkly")
        
    print("App is running")
    app.mainloop()
    