#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------
verbose = True

# Standard modules
import os
import time
import sys
# Related major packages
import project
import anuga
#from anuga.culvert_flows.culvert_class import Culvert_flow
#from anuga.culvert_flows.culvert_routines import boyd_generalised_culvert_model

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
#------------------------------------------------------------------------------
# Create the triangular mesh and domain based on
# overall clipping polygon with a tagged
# boundary and interior regions as defined in project.py
#------------------------------------------------------------------------------
bounding_polygon = anuga.read_polygon(project.configpath+'extent.csv')

meshname = project.tmppath+'output.msh'
mesh = anuga.create_mesh_from_regions(bounding_polygon,
	 boundary_tags={'top': [0],
        'east': [1],
        'bottom': [2],
        'west': [3]},
        maximum_triangle_area=project.default_res,
        filename=meshname,
        interior_regions=None,
        interior_holes=None,
        hole_tags=None,
        #breaklines = breaklines,
        breaklines = None,
        use_cache=False,
        verbose=True)
domain = anuga.Domain(meshname,use_cache=False,verbose = True)

inflow = anuga.Inflow(domain, center=(project.center), radius=project.radius, rate=project.rate)
domain.forcing_terms.append(inflow)


# Print some stats about mesh and domain
print 'Number of triangles = ', len(domain)
print 'The extent is ', domain.get_extent()
print domain.statistics()
#------------------------------------------------------------------------------
# Setup parameters of computational domain
#------------------------------------------------------------------------------
domain.set_name(project.outpath+'anuga_output') # Name of sww file
domain.set_datadir('.') # Store sww output here
domain.set_minimum_storable_height(0.01) # Store only depth > 1cm
#------------------------------------------------------------------------------
# Setup initial conditions
#------------------------------------------------------------------------------
tide = 0.0
domain.set_quantity('stage', -10)
domain.set_quantity('friction', 0.0)
domain.set_quantity('elevation',
	filename=project.tmppath+'dtm_utm.mean.pts',
	use_cache=True,
	verbose=True,
	alpha=0.1)

#for record in culverts:
#        culvert = Culvert_flow(domain,
#                label=record[1],
#                description='This culvert is a test unit',
#                end_point0=[record[2], record[3]],
#                end_point1=[record[4], record[5]],
#                width=record[6],
#                height=record[7],
#                culvert_routine=boyd_generalised_culvert_model,
#                number_of_barrels=1,
#                verbose=verbose)
#        domain.forcing_terms.append(culvert)

print 'Available boundary tags', domain.get_boundary_tags()
Bd = anuga.Dirichlet_boundary([tide, 0, 0]) # Mean water level
Bs = anuga.Transmissive_stage_zero_momentum_boundary(domain) # Neutral boundary
Br = anuga.Reflective_boundary(domain)
# Huge 50m wave starting after 60 seconds and lasting 1 hour.
Bw = anuga.Time_boundary(domain=domain,
function=lambda t: [(60<t<3660)*11, 0, 0])
domain.set_boundary({
	'east': Br,
	'bottom': Br,
	'west': Br,
	'top': Br})
#------------------------------------------------------------------------------
# Evolve system through time
#------------------------------------------------------------------------------
import time
t0 = time.time()
tend = project.tend
from numpy import allclose
scenario = 'fixed_wave'
name = project.outpath+'anuga_' + scenario
which_var = 2
if which_var == 0: # Stage
        outname = name + '_stage'
        quantityname = 'stage'
if which_var == 1: # Absolute Momentum
        outname = name + '_momentum'
        quantityname = '(xmomentum**2 + ymomentum**2)**0.5' #Absolute momentum
if which_var == 2: # Depth
        outname = name + '_depth'
        quantityname = 'stage-elevation' #Depth
if which_var == 3: # Speed
        outname = name + '_speed'
        quantityname = '(xmomentum**2 + ymomentum**2)**0.5/(stage-elevation+1.e-30)' #Speed
if which_var == 4: # Elevation
        outname = name + '_elevation'
        quantityname = 'elevation' #Elevation

# Save every 20 secs 
for t in domain.evolve(yieldstep=20, finaltime=tend):
	print domain.timestepping_statistics()
anuga.sww2dem(project.outpath+'anuga_output.sww',
       	outname+'.asc',
       	quantity=quantityname,
       	cellsize=0.5,
       	easting_min=627724,
       	easting_max=627893,
       	northing_min=5804634,
       	northing_max=5804828,
       	reduction=max,
       	verbose=False)

#print domain.boundary_statistics(tags='east')
# Save every 30 secs as wave starts inundating ashore
#for t in domain.evolve(yieldstep=100, finaltime=10000,
#		skip_initial_step=True):
#	print domain.timestepping_statistics()
#	print domain.boundary_statistics(tags='east')
print'.That took %.2f seconds' %(time.time()-t0)

