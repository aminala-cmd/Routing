import networkx as nx
from networkx import NetworkXNoPath
import osmnx as ox
import os
import geopandas as gpd

from shapely.geometry import MultiPoint,GeometryCollection,LineString


def nodes_to_linestring(path,graph):
    coords_list = [(graph.nodes[i]['x'],graph.nodes[i]['y']) for i in path]
    line = LineString(coords_list)
    return line

def shortest_path(orig_lat,orig_lng,dest_lat,dest_lng,G):
    orig_node,dist_to_orig_node = ox.distance.get_nearest_node(G,(orig_lat,orig_lng),method='haversine',return_dist=True)
    dest_node,dist_to_dest_node = ox.distance.get_nearest_node(G,(dest_lat,dest_lng),method='haversine',return_dist=True)
    
    dist_to_network = dist_to_orig_node + dist_to_dest_node
    
    shortest_path = nx.shortest_path(G,orig_node,dest_node)
    
    route = nodes_to_linestring(shortest_path,G)
    
    # transform to UTM
    
    return route

def find_route(row,graph):
    inc = row['geometry_x']
    off = row['geometry_y']
    
    orig_lat = inc.y
    orig_lng = inc.x
    
    dest_lat = off.y
    dest_lng = off.x
    
    
    return shortest_path(orig_lat,orig_lng,dest_lat,dest_lng,graph)


data_path = '/home/amina/blackbox/AA/Analyst'
incidences_path = 'incidences.shp'
offenders_path = 'Offenders.shp'
roads = 'roads.shp'

offenders_df = gpd.read_file(os.path.join(data_path,offenders_path))
inc_df = gpd.read_file(os.path.join(data_path,incidences_path))

offenders_sub = offenders_df[['id','geometry']]

offenders_sub.rename(columns={'id':'offenderid'},inplace=True)

offenders_sub.set_index('offenderid')

with_id = inc_df[ inc_df['offenderid']!=0 ]
# with_id
# take geometry object from offender and add it to incident dataframe
merged = with_id.merge(offenders_sub , on ='offenderid', how='right')

merged[~merged['geometry_x'].isna()]

# find bounding box to download data from osm from
multi_point = MultiPoint([g for g in inc_df.geometry])

offenders_multi_point = MultiPoint([g for g in offenders_df.geometry])

gc = GeometryCollection([multi_point,offenders_multi_point])
minx,miny,maxx,maxy = gc.bounds


region_graph = ox.graph_from_bbox(maxy, miny, minx, maxx, network_type='all', simplify=True)


for idx,row in merged[~merged['geometry_x'].isna()].iterrows():
    try:
        route = find_route(row,region_graph)
        merged.loc[idx,'route'] = route.wkt      
    except ValueError:
        pass
    except nx.NetworkXNoPath:
        pass


found = merged[~merged['route'].isna()][['route','offenderid']]

import shapely

found['geometry'] = found['route'].apply(lambda row: shapely.wkt.loads(row))
found = gpd.GeoDataFrame(found)
found['incident_id'] = found.index
found


plt,ax = ox.plot.plot_graph(region_graph)

merged.set_geometry('geometry_x').plot(ax=ax,color='green')
merged.set_geometry('geometry_y').plot(ax=ax,color='red')

plt


# export routes to file 
found[['incident_id','offenderid','geometry']].to_file('found_routes.gpkg',driver='GPKG')