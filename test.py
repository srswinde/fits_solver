from imsolve import mont4k
import json
import sys
import os

if len(sys.argv) == 1:
	
	path = '.'
	
elif len(sys.argv)  == 2:
	path = sys.argv[1]
	
data = []
files = [ fname for fname in os.listdir(path) if fname[-4:] == 'fits' ]
	
for imgname in sorted(files):

	print imgname

	solver = mont4k( imgname, indir=path )
	try:
		solver.solve_all()
	
		
		
	except(Exception):
		print "fuck this guy", imgname
		

	data.append(dict(solver))

print data 


json.dump( data , open('pointing.json', 'w'), indent=4 )
