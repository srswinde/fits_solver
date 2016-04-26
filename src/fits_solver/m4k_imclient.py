from scottSock import scottSock
import json
import time
from source_extraction import *
import tempfile


def main( imgname="ccd0163.fits", inDir='/home/scott/data', outDir="/home/scott/data/imserver" ):

	if inDir.endswith('/'): endDir = endDir[:-1]
	if outDir.endswith('/'): outDir = outDir[:-1]
	tname = writetmpfits( "{0}/{1}".format(inDir, imgname) )
	
	
	
	f=open(tname, 'rb')

	soc = scottSock( "nimoy", 9996  )

	soc.send( f.read() )


	while 1:
		try:
			meta = soc.recv( 256 )
			break
		except Exception:
			print "waiting"
		
	meta = json.loads( meta )





	data=""
	for key,val in meta['files'].iteritems():
		buffsize = 1024
		while 1:
			if val > buffsize:
				data+=soc.recv( buffsize )
				val-=buffsize
			else:
				data+=soc.recv(val)
				break
	
		tmpfd = open("table.{0}".format(key), 'wb')
		tmpfd.write( data )
		tmpfd.close()

		
	print meta

	soc.close()
	
if __name__ == '__main__':
	main()



