# **Vignette 3: Generating a ToxPi feature layer of COVID-19 vulnerability using ToxPi_creation_customized.py**  
Vignette 3 is a demonstration of method 1 in the map creation workflow using [Toxpi_creation_customized.py](../ToxPi_creation_customized.py) and Covid-19 vulnerability data for counties across the United States. The resulting map can be found [here](https://ncsu.maps.arcgis.com/home/item.html?id=1518637a0b454036a3d0d2fc8239ff08). The practice data used in this demonstration was already processed through steps 1A and 1B and can be found [here](../Examples/PracticeData/). It is suggested to use the subset as it will significantly reduce running time(Full ~ 1hour, Subset ~ 15min); however, if you would like to replicate Vignette 4 as well use the full dataset here as it is used in the hot spot analysis. A further description of the data can be found [here](https://www.niehs.nih.gov/research/programs/coronavirus/covid19pvi/details/).  

<p align = "center">
<img src="../Images/Vignette3.png" data-canonical-  
src="../Images/Vignette3.png" width="600" height="500" />  
</p>  

## Requirements:  
* ArcGIS Pro licensing  
* Requires being logged into ArcGIS Portal  
* Source column for data must be formatted Latitude, Longitude(See [Utilities](../Utilities/) for help if needed)    
* Column labeled Name with unique identifiers must be present in data  
* Slice names must not contain a special character followed by a number  
* FIPS column must be present  
* Windows Operating System  
* Lyrx file must be output to a separate location folder for new maps, else it will overwrite the previous map layers within the geodatabase  
* Slice names must be formatted from the output of the ToxPi GUI for proper symbology  
* Column names other than the [ToxPi Score, HClust Group, KMeans Group, Name, Longitude, Latitude, FIPS, Tract, casrn] should not be included unless they are slices  

## Steps:  
1A, 1B. Already done, download entire repository, results data are [here](../Examples/PracticeData/) in repository     
1C. Run [ToxPi_creation_customized.py](../ToxPi_creation_customized.py) from windows command prompt using the following commands and parameters  
Note: If you previosuly ran Vignette2, make sure to redownload the data file as it was altered in Vignette2
```
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv" (Used to load ArcGIS Pro environment, see troubleshooting if a custom installation was done)  
python location\ToxPi_creation.py inputfile outputfolder\outputfile.lyrx (Used to run script, replace location with path to file)  

Parameters:
* inputfile - The ToxPi GUI results file to draw ToxPi features from  
* outputfolder\outputfile.lyrx - The location for the result lyrx file output by the script. Please add folder and .lyrx   
```

* Example:  
<p align = "center">
<img src="../Images/ExampleCommandVignette3.PNG" data-canonical-  
src="../Images/ExampleCommandVignette3.PNG" width="1000" height="70" />  
</p>  

1D. Open .lyrx file in ArcGIS Pro  
1E. Share as a web map to ArcGIS Online  
<p align = "center">
<img src="../Images/MapShare.png" data-canonical-  
src="../Images/MapShare.png" width="600" height="100" />  
</p>  

## Output:  
  * Script makes a geodatabase in the location folder called ToxPiAuto.gdb containing necessary information for the layer file as well as intermediate feature layers 
  * Script outputs a layer file at outputfile.lyrx  
  * Sharing provides a web URL for the public to view your map  

## Map Details:    
Choropleth based on ToxPi Score  
Local and state level statistics  
Layer visibility based on zoom extent  
Interactive slices with custom popups  
Colored slices based on ToxPi GUI choices    
Toggleable maximum score rings  

## General Troubleshooting:  
* Error when accessing environment  
  * Make sure quotes are included  
  * The location to the proenv may be different if you did a custom installation location of ArcGIS Pro
    *  Path to proenv must be changed within quotes  
    *  Path to toolboxes in script at Lines 990 and 991 must be changed  
* Error when running script  
  * If a file not found error is given, try using the full file path for outputfile.lyrx instead of the current directory  
  * If location is your current directory, use .\ to reference the location   
  * Make sure .lyrx is present on outfile   
  * Make sure you are logged into ArcGIS Portal and have required ArcGIS Pro licensing  
  * Make sure nonessential columns are not present in data  
  * Make sure name column is present  
  * Make sure FIPS column is present  
* Mapping Incorrect  
  * Ensure source is formatted latitude, longitude. [swap_coordinates.py](../Utilities/Swap_Coordinates.py) is provided in Utilities folder if coordinates need to be swapped  
  * Each time script is run to generate a map a different directory should be used unless overwriting a previous map     

