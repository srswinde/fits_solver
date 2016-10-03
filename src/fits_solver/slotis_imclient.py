from scottSock import scottSock
import json
import time
from source_extraction import *
import tempfile
import sys
import os
import tempfile
from astropy.io import fits
from threading import Thread

class solverThread(Thread):
	def __init__( self, img ):
		Thread.__init__( self )
		self.solved=False
		self.img=img
		
	def run( self ):
		fitsfd = fits.open( self.img )
		resp = solvefitsfd( fitsfd, timeout=20.0 )
		if 'wcs' in resp.keys():
			addwcs( fitsfd, resp['wcs'] )
			self.solved = True



def solvefitsfd( img, extnum=0, port=9002, timeout=60.0):
	ra, dec = img[0].header['ra'] , img[0].header['dec']
	naxis1, naxis2 = img[extnum].header['naxis1'], img[extnum].header['naxis2']
	
	tblargs ={
		'ra':ra,
		'dec':dec,
		'npix1':naxis1,
		'npix2':naxis2,
	}
	
	objs = getobjects( img[0].data )
	
	fitstbl = mkfitstable( objs )
	for key, val in tblargs.iteritems():
		fitstbl.header[key] = val
		
	tname = tempfile.mktemp()
	fitstbl.writeto( tname )
	
	fitstbl_fd=open(tname, 'rb')
	
	fitstbl_fd=open(tname, 'rb')
	
	soc = scottSock( "nimoy", port  )
	
	soc.send( fitstbl_fd.read() )
	t0 = time.time()
	while 1:
		try:
			meta = soc.recv( 256 )
			break
		except Exception:
			pass
	
		if ( time.time() - t0 ) > timeout:
			return {}
			
	try:
		meta = json.loads( meta )
	except Exception as err:
		return {}

	outfits = {}
	for fname in meta['forder']:
		fsize = meta['files'][fname]
		data = ''		
		buffsize = 128
		#print "File is {} filesize if {}".format(fname,fsize)
		while 1:

			if fsize > buffsize:
				newData = soc.recv( buffsize )
				
				if len(newData) == 0:
					#print "Soc recieved no data for file {}".format(fname)
					#print "Buffer size is {} file has {} bytes left, data is {} bytes".format(buffsize, fsize, len(data))
					break
				
				data+=newData
				
				fsize-=len(newData)
			else:
				data+=soc.recv(fsize)
				break
			
		tempname = tempfile.mktemp()

		tmpfd = open( tempname, 'wb' )
		
		tmpfd.write( data )
		tmpfd.close()

		try:
			outfits[fname] = fits.open( tempname )
		except Exception as err:
			print "The file {} was not downloaded error was {}".format( fname, err )



	for key, val in meta.iteritems():
		if str(key) != "files" and str(key) != "forder":
			outfits[key] = val
			
			
			
	return outfits		
	
	
	
def addwcs( imgfd, wcsfd, imgext=0, wcsext=0 ):
	#add wcs and try to save in place
	for key, value in wcsfd[wcsext].header.iteritems():
		
		
		if key == "COMMENT":
			imgfd[imgext].header.add_comment( value )
			
		elif key == "HISTORY":
			imgfd[imgext].header.add_history( value )
		
		elif key in ['DATE', 'SIMPLE']:
		#dont replace these keys
			pass
			
		else:
		
			if key in imgfd[imgext].header:
				imgfd[imgext].header[key+'0'] = imgfd[imgext].header[key]
			
			
			if key != 'HISTORY':
				imgfd[imgext].header[key] = ( wcsfd[wcsext].header[key], "From astrometry.net" )
	
	

			
			
def main(img):
	fitsfd = fits.open( img, mode='update' )
	resp = solvefitsfd( fitsfd )
	solved = False
	if 'wcs' in resp.keys():
		solved = True
		addwcs( fitsfd, resp['wcs'] )
	
	fitsfd[0].header['FIXWCS'] = solved
	fitsfd.flush( output_verify='ignore' )
	

	return solved
	
def checkThreads( threadlist ):
	nsol=0
	nliveThreads = 0
	
	for thread in threadlist:
		if thread.solved : nsol+=1
		if thread.isAlive(): nliveThreads+=1

	return nsol, nliveThreads, len(threadlist) - nsol
	
if __name__ == '__main__':
	threads = []
	for img in sys.argv[1:]:
		solved = False
		t0 = time.time()
		fd = fits.open(img)
		thisThread = solverThread( img )
		thisThread.start()
		threads.append( thisThread )
		while (time.time() - t0) < 1.0:
			if not thisThread.isAlive():
				solved=True
				fd.close()
				thisThread.join()
				break

		
		nSolved, nLiveThreads, nNotSolved = checkThreads( threads )
		while nLiveThreads > 10:
			print "Too many Threads waiting a few seconds"
			nSolved, nLiveThreads, nNotSolved = checkThreads( threads )
			"{} solved, {} not soved, {} threads alive".format( nSolved, nNotSolved, nLiveThreads )
			
			time.sleep(1.0)
		
			
		
		print nSolved, "images were solved,", nNotSolved, "not solved,", nLiveThreads, "threads alive"

	if nLiveThreads > 0 :
		print "10 more seconds for solving"
		time.sleep(10.0)
	for thread in threads:
		if not thread.solved:
			print thread.img, "Not Solved"





