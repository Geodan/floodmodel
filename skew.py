import anuga.load_mesh.loadASCII as loadASCII



def skew(mesh):
	import math, numpy, random
	
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
			print '-----'
			print "Couldn't calculate normal"
			print a,b,c
			print U
			print V
			print N
			print factor
			print normal
			raise ValueError()
		return normal
		
	def geojson(a,b,c,area,i):    
		return '{"type": "Feature","properties": {"index": '+str(i)+',"area": '+str(area)+'},"geometry": {"type": "Polygon","coordinates": [[['+str(a[0])+','+str(a[1])+'],['+str(b[0])+','+str(b[1])+'],['+str(c[0])+','+str(c[1])+'],['+str(a[0])+','+str(a[1])+']]]}},\n'

	def getvertices(i):
		a = numpy.append(numpy.array(mesh['vertices'][mesh['triangles'][i][0]]),mesh['vertex_attributes'][mesh['triangles'][i][0]]) 
		b = numpy.append(numpy.array(mesh['vertices'][mesh['triangles'][i][1]]),mesh['vertex_attributes'][mesh['triangles'][i][1]])
		c = numpy.append(numpy.array(mesh['vertices'][mesh['triangles'][i][2]]),mesh['vertex_attributes'][mesh['triangles'][i][2]])
		return (a,b,c)
		
	def skew(i,n):  
		a,b,c = getvertices(i)
		zarray = [a[2], b[2],c[2]]
		zarray.sort()
		for v in range(3):
			vertex = mesh['triangles'][i][v]
			l = list(mesh['vertices'][vertex])
			z = mesh['vertex_attributes'][vertex]
			if mesh['vertex_attributes'][vertex] == zarray[2]:
				mesh['vertices'][vertex] = (l[0] - 0.002 * n[0],l[1] - 0.002 * n[1])
			elif mesh['vertex_attributes'][vertex] == zarray[1]:
				mesh['vertices'][vertex] = (l[0] - 0.001 * n[0],l[1] - 0.001 * n[1])
			elif mesh['vertex_attributes'][vertex] == zarray[0]:
				mesh['vertices'][vertex] = (l[0] + 0.001 * n[0],l[1] + 0.001 * n[1])
				pass
	
	def blow(i):
		a,b,c = getvertices(i)
		print '-----',i
		print a,b,c
		print 'area voor:' ,calcarea(a,b,c)
		xmax = numpy.max([a[0],b[0],c[0]])
		ymax = numpy.max([a[1],b[1],c[1]])
		xmin = numpy.min([a[0],b[0],c[0]])
		ymin = numpy.min([a[1],b[1],c[1]])
		center = [xmin+((xmax - xmin)/2),ymin+((ymax - ymin)/2)]
		for v in range(3):
			vertex = mesh['triangles'][i][v]
			l = list(mesh['vertices'][vertex])
			x = l[0]
			y = l[1]
			xd,yd=0,0
			if x > center[0]:
				xd = 1
			elif x < center[0]:
				xd = -1
			if y > center[1]:
				yd = 1
			elif y < center[1]:
				yd=-1
			mesh['vertices'][vertex] = (l[0] + 0.001 * xd,l[1] + 0.001 * yd)
		a,b,c = getvertices(i)
		print a,b,c
		print 'area na: ',calcarea(a,b,c)
	
	def skewloop(debug):
		print 'skewing'
		wrongs = 0
		trianglenr = len(mesh['triangles'])
		for i in range(trianglenr):
			if (i==11835 or i==11841):
				pass
			else:
				a,b,c = getvertices(i)
				area = calcarea(a,b,c)
				try:
					n = calcnormal(a,b,c)
				except ValueError:
					print 'bad vals: ',i,a,b,c
					#blow(i)
				if (n[2] <= 0 or area <=0):
					wrongs =wrongs+1
					skew(i,n) 
					if debug==True:
						print 'Triangle: ',i
						print getvertices(i)
						print n
		return wrongs

	def blowloop(debug):
		print 'blowing'
		trianglenr = len(mesh['triangles'])
		for i in range(trianglenr):
			a,b,c = getvertices(i)
			area = calcarea(a,b,c)
			n = calcnormal(a,b,c)
			if (n[2] <= 0 or area <=0):
				blow(i)
				
				
	counter = 0
	trianglenr = len(mesh['triangles'])
	for i in range(trianglenr):	
		a,b,c = getvertices(i)
		area = calcarea(a,b,c)
		fo1.write(geojson(a,b,c, area,i))
	
	wrongs = skewloop(False)
	print wrongs
	while wrongs > 5:
		counter = counter +1
		wrongs = skewloop(False)
		print wrongs
		if counter > 5:
			skewloop(True)
			#blowloop(True)
			break
		
	trianglenr = len(mesh['triangles'])
	for i in range(trianglenr):	
		a,b,c = getvertices(i)
		area = calcarea(a,b,c)
		fo.write(geojson(a,b,c, area,i))


allgood = False
mesh = loadASCII.import_mesh_file('output.msh')
fo1 = open("foo.geojson", "rw+")
fo = open("foo2.geojson", "rw+")
fo1.write('{"type": "FeatureCollection","features":[\n')
fo.write('{"type": "FeatureCollection","features":[\n')
skew(mesh)
fo.write(']}')
fo.close()
fo1.write(']}')
fo1.close()
loadASCII.export_mesh_file('output_skewed.msh',mesh)