#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------
verbose = True

# Standard modules
import os
import time
import sys
import json
import psycopg2
# Related major packages
import project
import anuga

# Application specific imports
#from floodpoint import *
#from polygons import *
#from breaklines import *
#from culverts import *

#------------------------------------------------------------------------------
# Preparation of topographic data
# Convert ASC 2 DEM 2 PTS using source data and store result in source data
#------------------------------------------------------------------------------
# Create DEM from asc data
anuga.asc2dem(project.tmppath + 'dtm_utm.mean.asc', use_cache=False, verbose=verbose)
# Create pts file for onshore DEM
anuga.dem2pts(project.tmppath + 'dtm_utm.mean.dem', use_cache=False, verbose=verbose)

bounding_polygon = anuga.read_polygon(project.configpath+'extent.csv')

#------------------------------------------------------------------------------
# Prepare breaklines
#
#------------------------------------------------------------------------------
conn_params = "host=titania dbname=research user=geodan"
conn = psycopg2.connect(conn_params)
cur = conn.cursor()
breaklines = []
querystring = """
WITH extent AS (
	SELECT ST_Transform(ST_SetSrid(ST_MakeEnvelope(%s),32631),28992) as geom
)

,transformed As(
	SELECT ST_Transform((ST_Dump(ST_Union(ST_SnapToGrid(ST_Intersection(geom,wkb_geometry),0.1)))).geom,32631) geom	
	FROM brt_201402.hoogteverschillz_lijn a, extent
	WHERE ST_Intersects(geom,wkb_geometry)
	UNION ALL
	SELECT ST_Transform((ST_Dump(ST_Intersection(geom,wkb_geometry))).geom,32631) geom	
	FROM brt_201402.hoogteverschilhz_lijn a, extent
	WHERE ST_Intersects(geom,wkb_geometry)
)
SELECT ST_AsGeoJson(St_Simplify(geom,0.5)) geom FROM transformed""" %(','.join(str(x) for x in (bounding_polygon[0]+bounding_polygon[2])))

cur.execute(querystring)
lines = cur.fetchall()
for record in lines:
	breakline = json.loads(record[0])["coordinates"]
	breaklines.append(breakline)



#------------------------------------------------------------------------------
# Prepare interior holes
#
#------------------------------------------------------------------------------
conn_params = "dbname=research user=geodan"
conn = psycopg2.connect(conn_params)
cur = conn.cursor()
querystring = """
WITH blocks AS (
SELECT ST_SimplifyPreserveTopology(ST_Union(wkb_geometry),0.5) geom
FROM bgt_import2.pand_2dactueelbestaand
WHERE ST_Contains(ST_Transform(ST_SetSrid(ST_MakeEnvelope(%s),32631),28992),wkb_geometry)
AND ST_Area(wkb_geometry) > 20
)
,dump AS (
SELECT (ST_Dump(geom)).geom FROM blocks
)
SELECT 
ST_AsGeoJson((ST_Dump(ST_Transform(geom,32631))).geom)
FROM dump
""" %(','.join(str(x) for x in (bounding_polygon[0]+bounding_polygon[2])))
cur.execute(querystring)
lines = cur.fetchall()
interior_holes = []
for record in lines:
		#Since we are dealing with multi polys, only take the first [0]
		coords = json.loads(record[0])["coordinates"][0]
		interior_holes.append(coords)

#------------------------------------------------------------------------------
# Prepare interior regions
#
#------------------------------------------------------------------------------
conn_params = "dbname=research user=geodan"
conn = psycopg2.connect(conn_params)
cur = conn.cursor()
querystring = """
WITH blocks AS (
SELECT ST_SimplifyPreserveTopology(ST_Union(wkb_geometry),0.5) geom
FROM bgt_import2.waterdeel_2dactueelbestaand
WHERE ST_Contains(ST_Transform(ST_SetSrid(ST_MakeEnvelope(%s),32631),28992),wkb_geometry)
)
,dump AS (
SELECT (ST_Dump(geom)).geom FROM blocks
)
SELECT 
ST_AsGeoJson((ST_Dump(ST_Transform(geom,32631))).geom)
FROM dump
""" %(','.join(str(x) for x in (bounding_polygon[0]+bounding_polygon[2])))
cur.execute(querystring)
lines = cur.fetchall()
interior_regions = []
for record in lines:
		#Since we are dealing with multi polys, only take the first [0]
		coords = json.loads(record[0])["coordinates"][0]
		interior_regions.append([coords,100])



#------------------------------------------------------------------------------
# Create the triangular mesh and domain based on
# overall clipping polygon with a tagged
# boundary and interior regions as defined in project.py
#------------------------------------------------------------------------------


meshname = project.tmppath+'output.msh'

mesh = anuga.create_mesh_from_regions(bounding_polygon,
	 boundary_tags={'top': [0],
        'east': [1],
        'bottom': [2],
        'west': [3]},
        maximum_triangle_area=project.default_res,
        filename=meshname,
        interior_regions=interior_regions,
        interior_holes=interior_holes,
        hole_tags=None,
        breaklines = breaklines,
        #breaklines = None,
        use_cache=False,
        verbose=True)
