# ToxPi\*GIS Toolkit
## **GitHub Description:**  
The following methods are used for the production and visualization of shareable, interactive feature layers containing ToxPi figures using ArcGIS Pro. Two methods are provided for production, labeled as 1 and 2 in the [Map Creation Workflow](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/README.md#map-creation-workflow) located below. [Method 1](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/README.md#method-1-toxpi_creationpy--toxpi_creation_customizedpy) uses a customized python script that can be run on the Windows Command Prompt to automatically produce a predesigned layer file of ToxPi features symbolized based on the ToxPi GUI output that can be opened within ArcGIS Pro and is ready to be shared to ArcGIS Online for visualization. This is the suggested method unless you are integrating the ToxPi features into a fully automated ArcGIS model. Examples of this process can be seen under [Vignette 1](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Vignette1:%20Using%20ToxPi_creation.md) and [Vignette 3](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Vignette3:%20Using%20ToxPi_creation_customized.md) in the Examples folder. For users looking to integrate ToxPi feature layers into already existing workflows or ArcGIS models, [Method 2](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/README.md#method-2-toxpitoolboxtbx) is provided which uses a custom ArcToolbox that can be added to ArcGIS Pro and used to produce symbolized ToxPi features. Use this method if you want to develop your own pipeline within ArcGIS Pro, your data does not fit the formatting required for use of the python script, or you only want to use a subset of the slices in your data. Examples of this process can be seen under [Vignette 2](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Vignette2:%20Using%20ToxPiToolbox.md) in the Examples folder. Practice data can be found within [Practice Data](https://github.com/Jonathon-Fleming/ToxPi-GIS/tree/main/Examples/Practice%20Data) in the Examples folder. If you are a user looking only to visualize maps created by other users, please see [Visualization Instructions](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/README.md#Visualization-Instructions) below and the examples under [Visualizations](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Visualizations.md) within the Examples folder.  
  
## **ToxPi Description:**  
(insert description and images of ToxPi Figures and statistics here).  
  
## **Map Creation Workflow:**  
<p align = "center">
<img src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapCreationWorkflow.PNG" data-canonical-  
src="https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Images/MapCreationWorkflow.PNG" width="600" height="300" />  
</p>  
  
## **Method 1: ToxPi_creation.py & ToxPi_creation_customized.py**   
Use the script [ToxPi_creation.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/ToxPi_creation.py)  to automatically produce predesigned feature layers containing interactive ToxPi features using the output of the ToxPi GUI as input. This is the suggested method, unless you are skilled with ArcGIS Pro and have a specific need for a Toolbox. An example walkthrough is shown in [Vignette 1](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Vignette1:%20Using%20ToxPi_creation.md). 
<br></br>
[ToxPi_creation_customized.py](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/ToxPi_creation_customized.py) can be used with county or census tract data for a more data rich map and acts as an example of how ToxPi_creation.py can be customized with further geoprocessing steps to create more advanced maps for specific data. An example walkthrough is shown in [Vignette 3](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Vignette3:%20Using%20ToxPi_creation_customized.md).  

Steps:  
1A. Load raw data into the [ToxPi GUI](https://toxpi.org/)  
1B. Analyze data and output results file to a CSV, and make sure file meets data requirements    
1C. Run python script from windows command prompt using the required parameters  
1D. Open output layer file in ArcGIS Pro  
1E. Share resulting map to ArcGIS Online  

## **Method 2: ToxPiToolbox.tbx**  
The ToxPiToolbox.tbx file is an ArcToolbox that contains a custom tool called ToxPi Construction for drawing the polygons that make up ToxPi figures. It requires more manual steps than the script; however, a model can be created for the automation of map creation, and the toolbox allows for more customization than the script, including drawing a subset of slices for ToxPi features. This, along with a walkthrough example, are described under [Vignette 2](https://github.com/Jonathon-Fleming/ToxPi-GIS/blob/main/Examples/Vignette2:%20Using%20ToxPiToolbox.md).  

Steps:  
2A. Load raw data into the [ToxPi GUI](https://toxpi.org/)  
2B. Analyze data and output results file to a CSV, and split the coordinates into two separate columns  
2C. Add results file to ArcGIS Pro  
2D. Add ToxPiToolbox.tbx to ArcGIS Pro  
2E. Run required analysis steps including the ToxPi tool and share resulting map to ArcGIS Online  

## **Utilities Folder:**  
This folder contains python scripts that may be useful for data manipulation and formatting requirements and can be run from the command line. None of the scripts are part of the pipeline; however, they may be useful if your data does not meet a methods requirements.  

## **Visualization Instructions:**  
(Discuss paths here, need to finalize what these are and the best way to present these)

## **References:**  

    
    
