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
5) Run this command:<br/>### On Windows
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
5) Before

## Annotation procedure
