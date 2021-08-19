# **Vignette 3: Generating a ToxPi feature layer of COVID-19 vulnerability using ToxPi_creation_customized.py**  
Vignette 3 is a demonstration of method 1 in the map creation workflow using [Toxpi_creation_customized.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/ToxPi_creation_customized.py) and Covid-19 vulnerability data for counties across the United States. The resulting map can be found [here](https://ncsu.maps.arcgis.com/home/item.html?id=1518637a0b454036a3d0d2fc8239ff08). The practice data used in this demonstration was already processed through steps 1A and 1B and can be found [here](https://github.com/Jonathon-Fleming/ToxPi-GIS/tree/main/Examples/Practice%20Data). It is suggested to use the subset as it will significantly reduce running time(Full ~ 1hour, Subset ~ 15min). A further description of the data can be found [here](https://www.niehs.nih.gov/research/programs/coronavirus/covid19pvi/details/).  

<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Vignette3.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/Vignette3.png" width="600" height="600" />  
</p>  

## Requirements:  
* ArcGIS Pro licensing  
* Requires being logged into ArcGIS Portal  
* Source column for data must be formatted Latitude, Longitude(See [Utilities](https://github.com/Jonathon-Fleming/ToxPi-GIS/tree/main/Utilities) for help if needed)    
* Column labeled Name with unique identifiers must be present in data  
* Slice names must not contain a special character followed by a number  
* FIPS column must be present  
* Windows Operating System  
* Lyrx file must be output to a separate location folder for new maps, else it will overwrite the previous map layers within the geodatabase  
* Slice names must be formatted from the output of the ToxPi GUI for proper symbology  
* Column names other than the [ToxPi Score, HClust Group, KMeans Group, Name, Longitude, Latitude, FIPS, Tract, casrn] should not be included unless they are slices  

## Steps:  
1A, 1B. Already done, download entire repository, results data are [here](https://github.com/Jonathon-Fleming/ToxPi-GIS/tree/main/Examples/Practice%20Data) in repository     
1C. Run [ToxPi_creation_customized.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/ToxPi_creation_customized.py) from windows command prompt using the following commands and parameters
```
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv" (Used to load ArcGIS Pro environment)  
python location\ToxPi_creation.py inputfile outputfile.lyrx (Used to run script, replace location with path to file)  

Parameters:
* inputfile - The ToxPi GUI results file to draw ToxPi features from  
* outputfile.lyrx - The location for the result lyrx file output by the script. Please add .lyrx   
```

* Example:  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ExampleCommandVignette3.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/ExampleCommandVignette3.PNG" width="1000" height="70" />  
</p>  

1D. Open .lyrx file in ArcGIS Pro  
1E. Share as a web map to ArcGIS Online  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapShare.png" width="600" height="100" />  
</p>  

## Output:  
  * Script makes a geodatabase in the location folder called ToxPiAuto.gdb containing necessary information for the layer file as well as intermediate feature layers 
  * Script outputs a layer file at outputfile.lyrx  
  * Sharing provides a web URL for the public to view your map  


## General Troubleshooting:  
* Error when accessing environment  
  * Make sure quotes are included  
  * The location to the proenv may be different if you did a custom installation location of ArcGIS Pro 
* Error when running script  
  * If a file not found error is given, try using the full file path for outputfile.lyrx instead of the current directory  
  * If location is your current directory, use .\ to reference the location   
  * Make sure .lyrx is present on outfile   
  * Make sure you are logged into ArcGIS Portal and have required ArcGIS Pro licensing  
  * Make sure nonessential columns are not present in data  
  * Make sure name column is present  
  * Make sure FIPS column is present  
* Mapping Incorrect  
  * Ensure source is formatted latitude, longitude. [swap_coordinates.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Utilities/Swap_Coordinates.py) is provided in Utilities folder if coordinates need to be swapped  
  * Each time script is run to generate a map a different directory should be used unless overwriting a previous map     

