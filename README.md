# Annotation tool setup and it's usage
## How to setup the annotation tool?
The most straightforward way is to utilize our preconfigured conda environment.
### On Windows
1) Clone or download the repository to your local folder.
2) Download Anaconda here:<br/>
   https://www.anaconda.com/download<br/>
   You'll need to provide your email address and click Submit. After that, you'll be able to download the installation files..
3) Install Anaconda.
4) Open the Anaconda PowerShell Prompt and navigate to the folder where you cloned the repository.
5) Run this command:<br/>
   ```
   conda env create -f environment_win.yml
   ```
6) Activate the environment you created by running this command: <br/>
    ```
    conda activate annotation-tool-env 
    ```
7) You should now be able to run the annotation tool. However, there are a few caveats. First, you need to parse the database containing the person records. You can do this using the following command:
   ```
   python parser.py <database_name> <output_json_name>
   ```
   **NOTE:** The parsing process can take a long time, especially on larger databases (4+ minutes). </br>Also, ensure that the folder ```<database_name>``` is in the same directory as ```annotation_tool.py```.

8) After successfully parsing the database, you can run the annotation tool as follows:
   ```
   python annotation_tool.py data_json=<parser_output_json>
   ```
   Additionally, you can add several flags to configure the annotation tool:
   ```
   parser=on <database_name> <output_json_name>
   ```
   Runs the parser before starting the annotation tool.
   ```
   theme=<dark/light>
   ```
   You can choose between two appearance options for the annotation tool: 'dark' and 'light'..
   ```
   webview=<pywebview/webbrowser>
   ```
   This concerns the module used for opening a Wiki link. The webbrowser module opens it in a standalone browser..

   Finally, put it all together:
   ```
   python annotation_tool.py parser=on <database_name> <output_json_name> theme=<dark/light> webview=<pywebview/webbrowser>
   ```
   #### Warning: Avoid using '=' in your file names. Also, use only file names (without extensions) in the previous commands. Suffixes such as .json are added automatically.

   You can also run the annotation tool from your favorite IDE. However, you need to open our directory in the IDE and modify a few lines in the annotation tool's     main function. These lines are marked with TODO comments.
   
### On Linux
1) Clone this repository.
2) Download and install the Anaconda package manager: https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html .
3) Run this command:<br/>
   ```
   conda env create -f annotation_tool_ubuntu.yml
   ```
4) Activate the environment by running this command: <br/>
    ```
    conda activate annotation-tool-env 
    ```
5) Before the first annotation, you need to parse the database containing the person records. To this only once. Use the following command:
   ```
   python parser.py <database_name> <output_json_name>
   ```
   **NOTE:** The parsing process can take a long time, especially on larger databases (4+ minutes). </br>Also, ensure that the folder ```<database_name>``` is in the same directory as ```annotation_tool.py```.

6) You are now ready to start the annotation tool. Example running script:  
   ```
   python annotation_tool.py data_json=<parser_output_json> webview=webbrowser
   ```
   There are other optional flags you can use to run the script. The following flag runs the parser before opening the annotation tool:
   ```
   parser=on <database_name> <output_json_name>
   ```
   This flag sets the backgorund color of the GUI:
   ```
   theme=<dark/light>
   ```
   And this flag changes between pywebview (better positioning of external pages) and webbrowser:
   ```
   webview=<pywebview/webbrowser>
   ```
   **NOTE:** Running the flag ```webview=webbrowser``` is recommended on Linux, because some on some distros ```webview=pywebview``` was shown to cause issues.

## Annotation procedure






### Annotation tool layout
![Example of an annotation tool session](./readme_graphics/annotation_tool_example2.png)

1) Database info - contains the current status of the annotation (annotated/partially annotated/fully annotated), person ID within the database and an information about the progress with respect to the current dataset.

2) First wikipedia paragraph - Preview of the first paragraph from the wikipedia page. 

3) Link to wikipedia website - Opens the wikipedia website for the person. 

4) Birth date - Box for entering the birth date data for the person. The blue toggle button should be unmarked if the birth date info is impossible to gather.

5) Pixel position of the person - The annotator should mark the correct bounding box in the photo (11) corresponding to the annotated person by clicking inside the correct green rectangle. <br>
If there is only one bounding box detected it is selected automatically and no action is required. If there is no green rectangles in the picture (11) or there are multiple, the annotator should pick the correct one by clicking on the nose of the annotated person. The inside of the rectangle turns green and red dot indicating the nose of the person appears. If there is no bounding box, only the red dot will appear.

6) Estimated year interval of image creation - Box for entering the estimated time of image creation. If the estimation is not possible, the blue toggle button should be unmarked.
<br>The annotator can fill one year (i.e. in the example shown in the picture - 2016 gathered from the caption (10)) or a range of years (i.e. when the caption says "Winston Churchill during the time of the Boer wars.")

7) This blue toggle button should be unmarked if external sources other than the wikipedia page were used for gathering the data.<br/>
**NOTE: Plain wikipedia page, the annotator is only allowed to click the link in (3) and scroll on the page that opens. NO FURTHER CLICKING IS ALLOWED.**<br/>
If the data were gathered from elsewhere, this checkbox must be unmarked.

8) Annotation shortcommings - If the annotator failed to gather any data, the shortcommings should be described in this textbox.

9) Control panel
   ![Example of an annotation tool session](./readme_graphics/control_panel.png)

   c) Lists the total number of photos for current person<br>
   Click to: <br>
   a) Go back to the previous annotation<br>
   b) Save current annotation<br>
   d) Skips to the next unanotated person <br>
   e) Goes to the next person according to the order of the database <br>

10) Image caption - caption extracted from the wikipedia page.

11) Image - The face or bounding box should be marked by clicking as described in point (5).


### Annotation process step-by-step guide

1) Look at the first paragraph of the wikipedia page - box (2), if there is a birth date, fill it in the box (4) - the date format should be (dd - mm - yyyy), all integers.

2) Look at the Image caption - box (10), if you can guess the year or range of years in which the photo was taken fill it in the box (6).

3) Pick the correct bounding box in the picture (11). If there is only one person in the picture with face marked by a green rectangle, which has a green filling, nothing needs to be done. Otherwise, click in the correct rectangle. You should click on the nose of the person being annotated.

4) If all the information about the person was successfully filled in, click the (b) button in control panel (9). The annotation is complete. The text in box (1) should change to "fully annotated". You can continue with the next annotation by clicking (e) button in the control panel (9).

5) If not click on the link inside the box (3) - Open wikipedia page. Try to deduce the birth date and year range in which the photo was taken from the wikipedia page which opens. **YOU ARE ONLY ALLOWED TO SCROLL ON THIS PAGE, NO CLICKING IS ALLOWED**. If you find the information you are looking for fill it in the boxes (4) and (6).

6) If you were not able to find information on the wikipedia page that opens from link (3), you may search for information elsewhere. **HOWEVER IF YOU DO UNMARK THE BLUE TOGGLE BUTTON IN (7)**.

8) Fill in all the necessary information, if possible. Unmark the blue toggle buttons in the boxes (4), (5) and (6) if the information in the specific box is unobtainable.

9) If there is any information missing note it in the textbox (8) - annotation shortcommings.

10) Click the (b) button in control panel (9). The annotation is complete. The text in box (1) should change to "fully annotated". You can continue with the next annotation by clicking (e) button in the control panel (9).

