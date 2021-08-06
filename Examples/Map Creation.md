# Description
All Vignettes use data from the Covid19 PVI Dashboard located within the NIH. The following demos use the new Model 12.4 with the data being current for June 24,2021. Under this model, risk components are split into four domains: Infection Rate, Population Concentration, Intervention Measures, and Health & Environment. Overall, these four domains are comprised of a total of fourteen categories displayed in the figure below, each with their correspondiong weight shown. This new model, unlike previous models, accounts for vaccine data within Intervention Measures, thus allowing for a more accurate representation of COVID19 risk. More information about the model, including underlying components for each slice category, can be found at the NIH [PVI Dashboard details page](https://www.niehs.nih.gov/research/programs/coronavirus/covid19pvi/details/).  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ToxPiInfo.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ToxPiInfo.png" width = "650" height = "350" />
</p>  

Although the demos use Model 12.4, these methods are compatible with any results file produced by the ToxPi GUI. Current results files for the PVI Dashboard can be found at the [PVI Dashboard data repository](https://github.com/COVID19PVI/data) which can be used in place of the practice files, or custom made results using the ToxPi GUI can be used.   

# Vignette 1(ToxPiCreation.py): Creating a ToxPi Feature Layer Using Python  
Description: Use the script ToxPiCreation.py to automatically produce predesigned feature layers containing interactive ToxPi features using the output of the ToxPi GUI as input. This is the suggested method, unless you are skilled with ArcGIS Pro and have a specific need for a Toolbox.
**Steps:**
* Download the root repository  
* Load the ArcGIS Pro environment using the following commmand  
    "%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv"
* Run the script using the vignette 1 subset test data(partial dataset will take roughly a few minutes whereas entire dataset will be about 20 minutes)  
    python ToxPiCreation.py Examples\PracticeData\Vignette1_Subset_NC.csv C:\Users\InputUser\Documents\Examples\Vignette1\Vignette1.lyrx 1.5
    
    Note: Script will produce ouput folder and vignette1 folder if they are not present  
* Open Vignette1.lyrx in ArcGIS Pro and share as a web map to ArcGIS Online
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png">
</p>  

* Obtain web link from ArcGIS Online via selecting the map in My Content and copying the URL or [view previously hosted map](https://ncsu.maps.arcgis.com/home/item.html?id=e524bb8f06984c36b325b4614d66f748)  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG">   
</p>  
* Optionally, edit descriptive elements and metadata for public viewing  

**Map Details:**  
Interactive slices with custom popups  
Colored slices based on ToxPi GUI choices  
Toggleable maximum score rings  
Sizing based on script parameters
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" width = "650" height = "300" />
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" width = "500" height = "300" />  
</p>  
<br/>  
# Vignette 2(ToxPiToolbox.tbx): Creating a ToxPi Feature Layer Using The ArcGIS Toolbox
Description: Use this method from within ArcGIS Pro to integrate ToxPi figures into your own analysis procedures that do not fit the above examples, as well as to allow custom ToxPi figure sizing or to draw only a subset of slices   

**Steps:**
* Download Vignette2 test data(Was obtained by using split_coordinates.py on Vignette1 test data to separate Latitiude and Longitude into separate columns)
* Open a new project in ArcGIS Pro(Project, New, Map, Change Name, Okay)  
* Add Vignette2 test data to the map(Map, Add Data, Vignette2_Subset_NC.csv)  
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
* Add ToxPiToolbox to project(Insert, Toolbox, Add Toolbox, ToxPiToolbox.tbx)  
* Turn on catalog pane(View, Catalog Pane)  
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

**Map Details:**  
Interactive slices  
Colored slices based on ToxPi GUI choices  
Toggleable maximum score rings  
Sizing based on input parameters  
Note: Special characters in slice names will be replaced by underscores  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/NonFIPSLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/NonFIPS.PNG" width = "550" height = "300" />  
</p>  

# Vignette 3(ToxPiModel.py): Altering ToxPiCreation.py for Advanced Map Creations  
Description: ToxPiModel.py is a demonstration of altering ToxPiCreation.py with more advanced analysis and geoprocessing steps to create new maps. This specific example is meant to be used with county or census tract data to create maps containing ToxPi feature layers and chorpleths that are visible based on zoom extent.

**Steps:**
* Download the root repository  
* Load the ArcGIS Pro environment using the following commmand  
    "%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv"
* Run the script using the vignette 1 subset test data(partial dataset will take roughly 5-10 minutes whereas entire dataset will be over an hour)  
    python ToxPiCreation.py Examples\PracticeData\Vignette1_Subset_NC.csv C:\Users\InputUser\Documents\Examples\Vignette3\Vignette3.lyrx
    
    Note: Script will produce ouput folder and vignette3 folder if they are not present  
* Open Vignette3.lyrx in ArcGIS Pro and share as a web map to ArcGIS Online
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png">
</p>  

* Obtain web link from ArcGIS Online via selecting the map in My Content and copying the URL or [view previously hosted map](https://ncsu.maps.arcgis.com/home/item.html?id=e524bb8f06984c36b325b4614d66f748)  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/WebLink.PNG">   
</p>  
* Optionally, edit descriptive elements and metadata for public viewing  

**Map Details:**  
Choropleth based on ToxPi Score  
Local and state level statistics  
Layer visibility based on zoom extent  
Interactive slices with custom popups  
Colored slices based on ToxPi GUI choices    
Toggleable maximum score rings  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/StateLayer.PNG" width = "650" height = "300" />
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/CountyLayer.PNG" width = "500" height = "300" />  
</p>  
<br/>  
