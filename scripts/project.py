tmppath = './tmp/'
configpath = './config/'
outpath = './output/'

#INFLOW
center = 610786,5753950
radius = 40
rate = 60

# bigger base_scale == less triangles
base_scale = 10 
default_res = 10 * base_scale
islands_res = base_scale
cairns_res = base_scale
shallow_res = 5 * base_scale

tend = 60 * 60 # one hour
yieldstep = 20 # two minutes