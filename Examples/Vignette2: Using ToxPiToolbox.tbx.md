Vignette 2 is a demonstration of method 2 in the map creation workflow using [ToxpiToolbox.tbx]() and Covid-19 vulnerability data. The resulting map visually matches Vignette 1, the output of ToxPi_creation.py. The data used in this demonstration was already processed through steps 1A and 1B and can be found [here](). A further description of the data can be found [here]().  

Requirements: 
* ArcGIS Pro licensing  
* Requires being logged into ArcGIS Portal  
* Basic knowledge of ArcGIS tools    
* Source column will likely need to be split into two separate coordinate columns  (See utilities folder for help formatting if needed)  
* Slice names must not contain a special character followed by a number 
  * Note: Special characters will be replaced by underscores in the output due to ArcGIS formatting  
* Windows Operating System   

**Steps:**  
2A. Already done  
2B. CSV file already generated [here](), but coordinates need to be split into two columns using any preferred method  
   * Split source column using [split_coordinates.py]() and the following command:
     ```
     python location\split_coordinates.py inputfile
     
     Parameters:
     * inputfile - The ToxPi GUI results file that has concatenated coordinates to be split  
     ````
   * Example: 
<p align = "center">  
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ExampleCommand.PNG" data-       canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ExampleCommand.PNG" width="900" height="70" />  
</p>  

2C. Load results file into an ArcGIS Pro map   
* Open a new project in ArcGIS Pro(Project, New, Map, Change Name, Okay)  
* Add test data to the map(Map, Add Data, Vignette2_Subset_NC.csv)  

2D. Load ToxPiToolbox into ArcGIS project  
* Add ToxPiToolbox to project(Insert, Toolbox, Add Toolbox, ToxPiToolbox.tbx)  
* Insert image here  

2E. Run required geoprocessing steps, including ToxPiToolbox, and share to ArcGIS Online  
* Open tool pane to search for tools(Analysis, Tools, Search for tool)  
* Add image here  
* Display data on the map using a projected coordinate system via the following tool and parameters:  
    Tool: Convert Coordinate Notation  
    Input Table: Vignette2_Subset_NC.csv  
    Input Coordinate System: GCS_WGS_1984  
    Output Feature Class: Vignette2_Displayed  
    Output Coordinate System: WGS_1984_Web_Mercator_Auxiliary_Sphere(Coordinate system needs to be projected, not geographic)  
        Note: To do this, select the globe, search WGS 1984 Web Mercator, drop down projected coordinate systems, drop down world, select WGS 1984 Web Mercator  
    Input Coordinate Format: DD2  
    X: Longitude  
    Y: Latitude  
    Output Coordinate Format: DD2  
    * Insert image here  
 
* Turn on catalog pane(View, Catalog Pane)  
  * Insert image here  
* Open custom script called ToxPi Construction from within ToxPiToolbox and run with desired parameters. The interface and parameter descriptions are shown below:  
<p align = "center"> 
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ToolInterface.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ToolInterface.PNG" width = "350" height = "500" />  
</p>   
<p align = "center">  
    inFeatures: Input feature layer to draw ToxPi figures from  <br>
    outFeatures: The desired name for the output ToxPi feature layer  <br>
    uniqueID: The column name for the unique identifier for locations  <br>
    inFields: The list of all desired fields to be included as slices  <br>
    inputWeights: A string of weights for determining each slices radial width in order, separated by ;  <br>
    inputRadius: A numerical value for determining the size of the drawn figures. The default is 1  <br>
    outFeaturesRings: The desired name for the max radius ring feature layer(optional) <br>
    </p>   
 * Complete further analysis or share your map to ArcGIS Online  
 * Insert image here  

Output:  
  * Toolbox generates a symbolized feature layer of ToxPi figures     
  * Sharing provides a web URL for the public to view your map  
