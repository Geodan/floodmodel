verbose = False

# Standard modules
import os
import time
import sys
import json
import project
import anuga

# The parallel interface
#from anuga import distribute, myid, numprocs, finalize, barrier
myid = 0

#from anuga.culvert_flows.culvert_class import Culvert_flow
#from anuga.culvert_flows.culvert_routines import boyd_generalised_culvert_model

meshname = project.tmppath+'output.msh'

#------------------------------------------------------------------------------
# Do the domain creation on processor 0
#------------------------------------------------------------------------------
print '##################### %i #########################' % myid
if anuga.myid == 0:
	domain = anuga.Domain(meshname,use_cache=False,verbose = verbose)
	inflow = anuga.Inflow(domain, center=(project.center), radius=project.radius, rate=project.rate)
	domain.forcing_terms.append(inflow)
else:
	domain = None

#------------------------------------------------------------------------------
# Now produce parallel domain
#------------------------------------------------------------------------------
domain = anuga.distribute(domain,verbose=verbose)

#domain.set_store_vertices_uniquely(False)

if anuga.myid == 0:
	# Print some stats about mesh and domain
	print 'Number of triangles = ', len(domain)
	print 'The extent is ', domain.get_extent()
	#print domain.statistics()
#------------------------------------------------------------------------------
# Setup parameters of computational domain
#------------------------------------------------------------------------------
domain.set_name(project.outpath+'anuga_output') # Name of sww file
domain.set_datadir('.') # Store sww output here
domain.set_minimum_storable_height(0.01) # Store only depth > 1cm
#------------------------------------------------------------------------------
# Setup initial conditions
#------------------------------------------------------------------------------

domain.set_quantity('stage', -2.0)
domain.set_quantity('friction', 0.0)
domain.set_quantity('elevation',
	filename=project.tmppath+'dtm_utm.mean.pts',
	use_cache=True,
	verbose=verbose,
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
tide = 1
print 'Available boundary tags', domain.get_boundary_tags()
Bd = anuga.Dirichlet_boundary([tide, 0, 0]) # Mean water level
Bs = anuga.Transmissive_stage_zero_momentum_boundary(domain) # Neutral boundary
Br = anuga.Reflective_boundary(domain)

domain.set_boundary({
	'top': Bs,
	'east': Bs,
	'bottom': Bs,
	'west': Bs,
	'interior': Br,
	'exterior': Br})
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
for t in domain.evolve(yieldstep=project.yieldstep, finaltime=tend):
	print domain.timestepping_statistics()
	
	
domain.sww_merge(verbose=True)



#print domain.boundary_statistics(tags='east')
# Save every 30 secs as wave starts inundating ashore
#for t in domain.evolve(yieldstep=100, finaltime=10000,
#		skip_initial_step=True):
#	print domain.timestepping_statistics()
#	print domain.boundary_statistics(tags='east')
if myid == 0:
	print'.That took %.2f seconds' %(time.time()-t0)
anuga.finalize()
