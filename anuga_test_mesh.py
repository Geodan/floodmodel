import numpy as num
import anuga
from anuga.load_mesh.loadASCII import *
from anuga.coordinate_transforms.geo_reference import Geo_reference
import anuga.load_mesh.loadASCII as loadASCII




file_name = "output_skewed.msh"
myid = 0
verbose = True

# The parallel interface
#from anuga import distribute, myid, numprocs, finalize, barrier


#------------------------------------------------------------------------------
# Do the domain creation on processor 0
#------------------------------------------------------------------------------
print '##################### %i #########################' % myid
if anuga.myid == 0:
	domain = anuga.Domain(mesh_filename=file_name)
	
	
	
else:
	domain = None

#------------------------------------------------------------------------------
# Now produce parallel domain
#------------------------------------------------------------------------------
domain = anuga.distribute(domain,verbose=verbose)

if anuga.myid == 0:
	# Print some stats about mesh and domain
	print 'Number of triangles = ', len(domain)
	print 'The extent is ', domain.get_extent()

domain.set_quantity('stage',-10)
domain.set_quantity('friction', 0.0)
Bd = anuga.Dirichlet_boundary([0,0,0])
Bs = anuga.Transmissive_stage_zero_momentum_boundary(domain)
Br = anuga.Reflective_boundary(domain)
domain.set_boundary(
	{'Border': Br,
	'exterior': Br,
	'30':Bd,
	'20':Bd,
	'50':Bd,
	'40':Bd}
)

from anuga.operators.rate_operators import Rate_operator
													#WORKING LOCATION!
op2 = Rate_operator(domain, rate=0.001, radius=3, center=( 84972.55,447517.54))
factor = 1e-3
#op3 = Rate_operator(domain, rate = 0.2, factor=factor)

for t in domain.evolve(yieldstep=10, finaltime=500):
	domain.report_water_volume_statistics()
	print domain.timestepping_statistics()
	
domain.sww_merge(verbose=True)
anuga.finalize()