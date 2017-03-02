import anuga.load_mesh.loadASCII as loadASCII
import math, numpy, random

def geojson(a,b,c,area,i):    
		return '{"type": "Feature","properties": {"index": '+str(i)+',"area": '+str(area)+'},"geometry": {"type": "Polygon","coordinates": [[['+str(a[0])+','+str(a[1])+'],['+str(b[0])+','+str(b[1])+'],['+str(c[0])+','+str(c[1])+'],['+str(a[0])+','+str(a[1])+']]]}},\n'
      
def calcarea3d(a,b,c):
	#determinant of matrix a
	def det(a):
		return a[0][0]*a[1][1]*a[2][2] + a[0][1]*a[1][2]*a[2][0] + a[0][2]*a[1][0]*a[2][1] - a[0][2]*a[1][1]*a[2][0] - a[0][1]*a[1][0]*a[2][2] - a[0][0]*a[1][2]*a[2][1]
	
	#unit normal vector of plane defined by points a, b, and c
	def unit_normal(a, b, c):
		x = det([[1,a[1],a[2]],
				 [1,b[1],b[2]],
				 [1,c[1],c[2]]])
		y = det([[a[0],1,a[2]],
				 [b[0],1,b[2]],
				 [c[0],1,c[2]]])
		z = det([[a[0],a[1],1],
				 [b[0],b[1],1],
				 [c[0],c[1],1]])
		magnitude = (x**2 + y**2 + z**2)**.5
		return (x/magnitude, y/magnitude, z/magnitude)
	
	#dot product of vectors a and b
	def dot(a, b):
		return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
	
	#cross product of vectors a and b
	def cross(a, b):
		x = a[1] * b[2] - a[2] * b[1]
		y = a[2] * b[0] - a[0] * b[2]
		z = a[0] * b[1] - a[1] * b[0]
		return (x, y, z)
	
	#area of polygon poly
	def area(poly):
		if len(poly) < 3: # not a plane - no area
			return 0
	
		total = [0, 0, 0]
		for i in range(len(poly)):
			vi1 = poly[i]
			if i is len(poly)-1:
				vi2 = poly[0]
			else:
				vi2 = poly[i+1]
			prod = cross(vi1, vi2)
			total[0] += prod[0]
			total[1] += prod[1]
			total[2] += prod[2]
		result = dot(total, unit_normal(poly[0], poly[1], poly[2]))
		return abs(result/2)
	return area([a,b,c])

def calcarea(a, b, c):
	x0 = a[0]
	y0 = a[1]
	x1 = b[0]
	y1 = b[1]
	x2 = c[0]
	y2 = c[1]
	return -((x1*y0-x0*y1) + (x2*y1-x1*y2) + (x0*y2-x2*y0))/2.0

def calcnormal(a,b,c):
	U = [0,0,0]
	V = [0,0,0]
	N = [0,0,0]
	U[0]=b[0] - a[0]
	U[1]=b[1] - a[1]
	U[2]=b[2] - a[2]
	
	V[0]=c[0] - a[0]
	V[1]=c[1] - a[1]
	V[2]=c[2] - a[2]
	
	N[0]=U[1]*V[2] - U[2]*V[1]
	N[1]=U[2]*V[0] - U[0]*V[2]
	N[2]=U[0]*V[1] - U[1]*V[0]
	factor = math.sqrt(N[0]**2 + N[1]**2 + N[2]**2)
	normal = (N[0]/factor,N[1]/factor,N[2]/factor)
	if (numpy.isnan(normal[0]) or numpy.isnan(normal[0]) or numpy.isnan(normal[0])):
		raise ValueError()
	return normal

def getvertices(i):
	a = numpy.append(numpy.array(mesh['vertices'][mesh['triangles'][i][0]]),mesh['vertex_attributes'][mesh['triangles'][i][0]]) 
	b = numpy.append(numpy.array(mesh['vertices'][mesh['triangles'][i][1]]),mesh['vertex_attributes'][mesh['triangles'][i][1]])
	c = numpy.append(numpy.array(mesh['vertices'][mesh['triangles'][i][2]]),mesh['vertex_attributes'][mesh['triangles'][i][2]])
	return (a,b,c)

def skew():
	for k in range(len(fixable)):
		i = fixable[k]
		a,b,c = getvertices(i)
		n = calcnormal(a,b,c)
		zarray = [a[2], b[2],c[2]]
		zarray.sort()
		for v in range(3):
			vertex = mesh['triangles'][i][v]
			l = list(mesh['vertices'][vertex])
			z = mesh['vertex_attributes'][vertex]
			if mesh['vertex_attributes'][vertex] == zarray[2]:
				mesh['vertices'][vertex] = (l[0] - 0.02 * n[0],l[1] - 0.02 * n[1])
			elif mesh['vertex_attributes'][vertex] == zarray[1]:
				mesh['vertices'][vertex] = (l[0] - 0.01 * n[0],l[1] - 0.01 * n[1])
			elif mesh['vertex_attributes'][vertex] == zarray[0]:
				mesh['vertices'][vertex] = (l[0] + 0.01 * n[0],l[1] + 0.01 * n[1])
				pass

def inflate():
	for k in range(len(inflatable)):
		i = inflatable[k]
		a,b,c = getvertices(i)
		n = calcnormal(a,b,c)
		area = calcarea(a,b,c)
		#print 'area voor:' ,area
		#print a,b,c
		#if area >0:
		#	print '!!!!!'
		#	break
		xmax = numpy.max([a[0],b[0],c[0]])
		ymax = numpy.max([a[1],b[1],c[1]])
		xmin = numpy.min([a[0],b[0],c[0]])
		ymin = numpy.min([a[1],b[1],c[1]])
		center = [xmin+((xmax - xmin)/2),ymin+((ymax - ymin)/2)]
		xc = center[0]
		yc = center[1]
		for v in range(3):
			vertex = mesh['triangles'][i][v]
			l = list(mesh['vertices'][vertex])
			x = l[0]
			y = l[1]
			dx = x - xc
			dy = y - yc
			f = math.sqrt(dx**2 + dy**2)
			xN = dx/f
			yN = dy/f
			mesh['vertices'][vertex] = (l[0] - 0.01 * xN,l[1] - 0.01 * yN)
			mesh['vertex_attributes'][vertex] = mesh['vertex_attributes'][vertex] + 0.01 
		a,b,c = getvertices(i)
		#print a,b,c
		#print 'area na: ',calcarea(a,b,c)

def remove(removeable):
	print 'Removing ', removeable
	mesh['triangles'] = numpy.delete(mesh['triangles'],removeable,0).tolist()
	mesh['triangle_neighbors'] = numpy.delete(mesh['triangle_neighbors'],removeable,0).tolist()
	mesh['triangle_tags'] = numpy.delete(mesh['triangle_tags'],removeable,0).tolist()
	

def check(mesh):
	trianglenr = len(mesh['triangles'])
	for i in range(trianglenr):
		a,b,c = getvertices(i)
		area = calcarea(a,b,c)
		area3D = calcarea3d(a,b,c)
		#Only when 2D area is 0 or smaller we have a problem
		if area <= 0:
			if area3D <=0:
				#it is overturned or corrupt, remove it
				removeable.append(i)
			else:
				try:
					n = calcnormal(a,b,c)
					if n[2] == 0:
						#It is vertical,skew it
						fixable.append(i)
					elif n[2] == 1 :
						#It has a very small horizontal surface, remove it 
						#inflatable.append(i)
						removeable.append(i)
					elif n[2] < 0:
						#It is overturned, remove it
						removeable.append(i)
					else: 
						#Just a small triangle
						#print "We shoulnd't get here" 
						removeable.append(i)
				except ValueError:
					#must be corrupt
					removeable.append(i)
	return len(corrupt)+len(fixable)+len(inflatable) + len(removeable)

#START
fixable = []
inflatable = []
removeable = []
corrupt = []
counter = 0
mesh = loadASCII.import_mesh_file('output.msh')
fo1 = open("foo.geojson", "rw+")
fo1.write('{"type": "FeatureCollection","features":[\n')
#do first check
wrongs = check(mesh)	
print 'Fixable: ',len(fixable)
print 'Inflatable: ',len(inflatable)
print 'Corrupt: ',len(corrupt)
print 'Removeable: ', len(removeable)

#keep looping until fixed
while wrongs > 0:
	print '-----',counter
	#inflate()
	skew()
	#fix()
	fixable = []
	inflatable = []
	removeable = []
	corrupt = []
	wrongs = check(mesh)
	counter = counter +1
	print 'Skewable: ',len(fixable)
	print 'Inflatable: ',len(inflatable)
	print 'Removeable: ', len(removeable)
	print 'Corrupt: ',len(corrupt)
	print 'Total: ',wrongs
	if counter > 1:
		print 'Too many loops (5), quitting...'
		break
#remove all remaining invalid triangles
removeable = corrupt+fixable+inflatable +removeable
remove(removeable)
wrongs = check(mesh)
print 'Last check: ' ,wrongs
trianglenr = len(mesh['triangles'])
for i in range(trianglenr):	
	a,b,c = getvertices(i)
	area = calcarea(a,b,c)
	fo1.write(geojson(a,b,c, area,i))
fo1.write(']}')
fo1.close()
loadASCII.export_mesh_file('output_skewed.msh',mesh)
print 'done'