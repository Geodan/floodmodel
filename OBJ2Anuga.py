from netCDF4 import Dataset
import numpy as num
import sys
import timeit

fname = "output.obj"

def string_to_char(l):
    '''Convert 1-D list of strings to 2-D list of chars.'''

    if not l:
        return []

    if l == ['']:
        l = [' ']

    maxlen = reduce(max, map(len, l))
    ll = [x.ljust(maxlen) for x in l]
    result = []
    for s in ll:
        result.append([x for x in s])
    return result
    
def readOBJ(mesh):
    data = open(fname,'r')

    try:
        while True:
            line = data.next()
            e = line.strip().split()
            if e[0]=="v":    
                #print "vertex"
                e.pop(0)
                e_f = map(float,e)
                mesh['vertices'].append((e_f[0],e_f[1]))
                mesh['vertex_attributes'][0].append([e_f[2]])

            if e[0]=="usemtl":
                classname = e[1]
                if e[1]=="Building":
                    #print "building"
                    continue
                else:
                    while True:
                        e = data.next().strip().split()
                        if len(e)==0:
                            break
                        if e[0]=="f":
                            e.pop(0)
                            mesh['triangles'].append(map(int,(int(e[0])-1, int(e[1])-1, int(e[2])-1)))
                            mesh['triangle_tags'].append(classname)
                        if e[0]=="o":
                            break
                        else:
                            continue
                
    except(StopIteration):
        print "stop"
        
def findNeighbors(mesh):
	
    trianglenr = len(mesh['triangles'])
    for i in range(trianglenr):
        neighbor0 = next((index for index, tri in enumerate(mesh['triangles']) if mesh['triangles'][i] is not tri and mesh['triangles'][i][0] in tri and mesh['triangles'][i][1] in tri), None)
        if not neighbor0:
            neighbor0 = -1
            mesh['segments'].append((mesh['triangles'][i][1], mesh['triangles'][i][0]))
            mesh['segment_tags'].append('Border')
            segmentpoints.append((mesh['vertices'][mesh['triangles'][i][1]], mesh['vertices'][mesh['triangles'][i][0]]))

        neighbor1 = next((index for index, tri in enumerate(mesh['triangles']) if mesh['triangles'][i] is not tri and mesh['triangles'][i][1] in tri and mesh['triangles'][i][2] in tri), None)
        if not neighbor1:
            neighbor1 = -1
            mesh['segments'].append((mesh['triangles'][i][2], mesh['triangles'][i][1]))
            mesh['segment_tags'].append('Border')
            segmentpoints.append((mesh['vertices'][mesh['triangles'][i][2]], mesh['vertices'][mesh['triangles'][i][1]]))
            
        neighbor2 = next((index for index, tri in enumerate(mesh['triangles']) if mesh['triangles'][i] is not tri and mesh['triangles'][i][2] in tri and mesh['triangles'][i][0] in tri), None)
        if not neighbor2:
            neighbor2 = -1
            mesh['segments'].append((mesh['triangles'][i][0], mesh['triangles'][i][2]))
            mesh['segment_tags'].append('Border')
            segmentpoints.append((mesh['vertices'][mesh['triangles'][i][0]], mesh['vertices'][mesh['triangles'][i][2]]))

        mesh['triangle_neighbors'].append((neighbor0, neighbor1, neighbor2))
        
        sys.stdout.write('%d%%\r' % (100 * (i / float(trianglenr))))
        sys.stdout.flush()
    print '100%'

def fixMesh(mesh):
    #the triangulation
    mesh['vertices'] = num.array(mesh['vertices'], num.float)
    mesh['vertex_attribute_titles'] = \
        num.array(string_to_char(mesh['vertex_attribute_titles']), num.character)

    num_attributes = len(mesh['vertex_attribute_titles'])
    num_vertices = mesh['vertices'].shape[0]
    if mesh['vertex_attributes'] != None:
        mesh['vertex_attributes'] = \
            num.array(mesh['vertex_attributes'], num.float)

    if num_attributes > 0 :
        mesh['vertex_attributes'] = \
            num.reshape(mesh['vertex_attributes'],(num_vertices,-1))

    mesh['segments'] = num.array(mesh['segments'], IntType)
    mesh['segment_tags'] = num.array(string_to_char(mesh['segment_tags']),
                                     num.character)
                                     
    mesh['triangles'] = num.array(mesh['triangles'], IntType)
    mesh['triangle_tags'] = num.array(string_to_char(mesh['triangle_tags']),
                                      num.character)
    mesh['triangle_neighbors'] = num.array(mesh['triangle_neighbors'], IntType)

    #the outline
    #mesh['points'] = num.array(mesh['points'], num.float)
    #mesh['point_attributes'] = num.array(mesh['point_attributes'], num.float)
    #mesh['outline_segments'] = num.array(mesh['outline_segments'], IntType)
    #mesh['outline_segment_tags'] = \
    #    num.array(string_to_char(mesh['outline_segment_tags']), num.character)
    #mesh['holes'] = num.array(mesh['holes'], num.float)
    #mesh['regions'] = num.array(mesh['regions'], num.float)
    #mesh['region_tags'] = num.array(string_to_char(mesh['region_tags']), num.character)
    #mesh['region_max_areas'] = num.array(mesh['region_max_areas'], num.float)

def writeMsh(ofilename, mesh):
    outfile = Dataset(ofilename, 'w', format='NETCDF3_64BIT')

    #Create new file
    outfile.institution = 'Geoscience Australia'
    outfile.description = 'NetCDF format for compact and portable storage ' + \
                          'of spatial point data'

    # dimension definitions - fixed
    outfile.createDimension('num_of_dimensions', 2)     # This is 2d data
    outfile.createDimension('num_of_segment_ends', 2)   # Segs have two points
    outfile.createDimension('num_of_triangle_vertices', 3)
    outfile.createDimension('num_of_triangle_faces', 3)
    outfile.createDimension('num_of_region_max_area', 1)

    # Create dimensions, variables and set the variables

    # trianglulation
    # vertices
    if (mesh['vertices'].shape[0] > 0):
        outfile.createDimension('num_of_vertices', mesh['vertices'].shape[0])
        outfile.createVariable('vertices', netcdf_float, ('num_of_vertices',
                                                          'num_of_dimensions'))
        outfile.variables['vertices'][:] = mesh['vertices']

        #print 'mesh vertex attributes', mesh['vertex_attributes'].shape
        
        if (mesh['vertex_attributes'] is not None and
            (mesh['vertex_attributes'].shape[0] > 0 and
             mesh['vertex_attributes'].shape[1] > 0)):
            outfile.createDimension('num_of_vertex_attributes',
                                    mesh['vertex_attributes'].shape[1])
            outfile.createDimension('num_of_vertex_attribute_title_chars',
                                    mesh['vertex_attribute_titles'].shape[1])
            outfile.createVariable('vertex_attributes',
                                   netcdf_float,
                                   ('num_of_vertices',
                                    'num_of_vertex_attributes'))
            outfile.createVariable('vertex_attribute_titles',
                                   netcdf_char,
                                   ('num_of_vertex_attributes',
                                    'num_of_vertex_attribute_title_chars'))
            outfile.variables['vertex_attributes'][:] = \
                                     mesh['vertex_attributes']
            outfile.variables['vertex_attribute_titles'][:] = \
                                     mesh['vertex_attribute_titles']

    # segments
    if (mesh['segments'].shape[0] > 0):
        outfile.createDimension('num_of_segments', mesh['segments'].shape[0])
        outfile.createVariable('segments', netcdf_int,
                               ('num_of_segments', 'num_of_segment_ends'))
        outfile.variables['segments'][:] = mesh['segments']
        if (mesh['segment_tags'].shape[1] > 0):
            outfile.createDimension('num_of_segment_tag_chars',
                                    mesh['segment_tags'].shape[1])
            outfile.createVariable('segment_tags',
                                   netcdf_char,
                                   ('num_of_segments',
                                    'num_of_segment_tag_chars'))
            outfile.variables['segment_tags'][:] = mesh['segment_tags']

    # triangles
    if (mesh['triangles'].shape[0] > 0):
        outfile.createDimension('num_of_triangles', mesh['triangles'].shape[0])
        outfile.createVariable('triangles', netcdf_int,
                               ('num_of_triangles', 'num_of_triangle_vertices'))
        outfile.createVariable('triangle_neighbors', netcdf_int,
                               ('num_of_triangles', 'num_of_triangle_faces'))
        outfile.variables['triangles'][:] = mesh['triangles']
        outfile.variables['triangle_neighbors'][:] = mesh['triangle_neighbors']
        if (mesh['triangle_tags'] is not None and
            (mesh['triangle_tags'].shape[1] > 0)):
            outfile.createDimension('num_of_triangle_tag_chars',
                                    mesh['triangle_tags'].shape[1])
            outfile.createVariable('triangle_tags', netcdf_char,
                                   ('num_of_triangles',
                                    'num_of_triangle_tag_chars'))
            outfile.variables['triangle_tags'][:] = mesh['triangle_tags']

###########################
netcdf_char = 'c'
netcdf_byte = 'b'
netcdf_int = 'i'
netcdf_float = 'd'
netcdf_float64 = 'd'
netcdf_float32 = 'f'
IntType = num.int32

segmentpoints = []
### create mesh
mesh = {}
mesh['vertices'] = []
mesh['vertex_attribute_titles'] = ['elevation']
mesh['vertex_attributes'] = [[]]
mesh['segments'] = []
mesh['segment_tags'] = []
mesh['triangles'] = []
mesh['triangle_tags'] = []
mesh['triangle_neighbors'] = []

readOBJ(mesh)
findNeighbors(mesh)
fixMesh(mesh)

#wktstr = ''
#for sp in segmentpoints:
#    wktstr += '({} {}, {} {}),'.format(sp[0][0], sp[0][1], sp[1][0], sp[1][1])
#print 'MULTILINESTRING(' + wktstr[:-1] + ')'

ofile = fname[:-4] + ".msh"
writeMsh(ofile, mesh)
