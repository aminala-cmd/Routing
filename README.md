# Routing
This is a script that computes the routes for various offender locations to their corresponding incidence location. The script utilizes  OSMNx and NetworkX to compute distances between points

# Scenario
In order to acquire the possible routes between offender and incidence, you have to match an offender location to an incidence location. In this case, one offender can have many incidences committed. So, for each of the incidences committed by an offender, a route will be computed.

# Configuration for localhost
Clone this repo using
git clone https://github.com/aminala-cmd/Routing.git
Install requirements
pip install -r requirements

# Running the script
Run the application using e.g python3 kibera_route_finder.py
Change the name of the script depending on the area on interest i.e Kibera or Mathare

# Outputs
The outputs will be a GeoPackage data format for the computed routes between offender locations and incidence points.




