# safe_cycle

As of July 31, in 2019 there have been 2,481 bicycle related injuries and 18 bicyclist deaths in New York City. In addition, a 2017 study [1] found that 89% of cyclist fatalities or serious injuries occur at intersections. The goal of this project is to understand what factors most influence the accident rate between cars and bicycles at intersections and, importantly, what types of infrastructure are best suited to address the issue at any given intersection. 

This project is, in addition, motivated by the existance of an international project called **Vision Zero**, whose goal is to eliminate traffic related injuries and deaths worldwide. Beginning in 2014, the city of New York has been partnering with Vision Zero to implement safety infrastructure projects citywide in order to meet the goals of Vision Zero. Conveniently, these projects are enumerated in various publicly available datasets at https://opendata.cityofnewyork.us/. 

## Results of the model and details of the analysis

### Contents

The majority of the analysis is present in the `Notebooks` folder, the contents of which are:

* `safe_cycle_2018_model.ipynb`: This is the model exploration notebook. In it I apply various forms of regression and classification algorithms to the intersection data and elaborate on the results.
* `safe_cycle_2018_data.ipynb`: This notebook contains the analysis that maps the Collision data set along with the Vision Zero implementation datasets to intersection locations 
* `Traffic_Signals.ipynb`: This notebook has some basic data exploration of the bicycle collision and intersection data.
* `safe_cycle_bike_trips.ipynb`: In this notebook I query the a SQL database `NYC_bikes_2018.sqlite` in order to create a pandas dataframe of aggregated bike traffic volumes. 
* `safe_cycle_bike_trips_hourly.ipynb`: Similar to the above, except attempting to refine based on hourly traffic patterns.
* `vehicle_traffic.ipynb`: This notebook analyzes the traffic data provided at https://opendata.cityofnewyork.us/. In particular, the street segments are mapped to geometry objects using the LION lines dataset at https://data.cityofnewyork.us/City-Government/LION/2v4z-66xt.

Data Sources

* The list of intersections were obtained as a geojson file using the traffic_signals tag in QGIS. 
* Bike traffic data was pulled from https://www.citibikenyc.com/system-data.



[1] Getman, A., L. Gordon-Koven, S. Hostetter, and R. Viola. Safer Cycling: Bicycle Ridership and Safety in New York City, 2017. New York City Department of Transportation.
