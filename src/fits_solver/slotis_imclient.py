#!/usr/bin/python

from scottSock import scottSock
import json
import time
import fits_solver
from fits_solver.source_extraction import *
import tempfile
import sys
import os
import tempfile
from astropy.io import fits
from threading import Thread
import warnings
import argparse

class solverThread(Thread):
	"""This threaded class redueces and image to a fitstble of
	pixel locations and fwhm and sends that table of to the 
	image server located at at the host given in the args"""

	def __init__( self, img, host, port, timeout, **solargs ):
		"""Constructor, simply gathers arguments and makes them 
		availabe to the rest of the class"""
		Thread.__init__( self )
		self.solved=None
		self.img=img
		self.host=host
		self.port=port
		self.timeout = timeout
		self.solargs=solargs

	def run( self ):
		"""Thread starts here. We do some setup, call solvefitsfd,
		and add the wcs data to the header if we get a solution"""

		self.t0=time.time()
		self.tend=None
		fitsfd = fits.open( self.img, mode="update" )
		fitsfd[0].header["FIXWCS"] = 0
		fitsfd.flush()
		resp = self.solvefitsfd( fitsfd,  )
		if 'solved' in resp.keys() and resp['solved'] == True:
			with warnings.catch_warnings():
				warnings.simplefilter("ignore")
			
				fitsfd[0].header["FIXWCS"] = 1
				fitsfd.flush()
				addwcs( fitsfd, resp['wcs'] )
			self.solved = True
			fitsfd.writeto( "w{}".format( self.img ), clobber=True )
		else:
			self.solved=False
		self.tend=time.time()

	def solvefitsfd(self, img, extnum=0 ):
		"""The bulk of the work is done here. We source extract with 
		with source_extracion (which uses SEP), create our fits table,
		send add usefull args to the fits header and send it to the server.
		"""
		
		#Grab the ra,dec and naxis values from fits header
		ra, dec = img[0].header['ra'] , img[0].header['dec']
		naxis1, naxis2 = img[extnum].header['naxis1'], img[extnum].header['naxis2']
		
		#build the fits header dictionary
		tblargs ={
			'ra':ra,
			'dec':dec,
			'npix1':naxis1,
			'npix2':naxis2,
			'timeout':self.timeout #timeout tells the server when to give up.
		}
		
		for argname, argvalue in self.solargs.iteritems():
			tblargs[argname] = argvalue

		#build the fits table
		objs = getobjects( img[0].data )
		self.objs = listify( objs )
		fitstbl = mkfitstable( objs )
	
		for key, val in tblargs.iteritems():
			fitstbl.header[key] = val
		
		
		tname = tempfile.mktemp()
		fitstbl.writeto( tname )
		fitstbl_fd=open(tname, 'rb')
	
		fitstbl_fd=open(tname, 'rb')
		
		#send the fits table to the server
		soc = scottSock( self.host, self.port )
		soc.send( fitstbl_fd.read() )
		
		t0 = time.time()

		
		#read the first 256 bytes, which contains helpfull metadata
		while 1:
			try:
				meta = soc.recv( 256 )
				break
			except Exception:
				pass
			time.sleep(0.01)
			if ( time.time() - t0 ) > self.timeout:
				return {}
			
		try:
			meta = json.loads( meta )
		except Exception as err:
			return {}

		#read the return data which hopefully will
		#contain some files stacked on top of eachother
		#each file is listed in the metadata along 
		#with its file size. 
		outfits = {}
		for fname in meta['forder']:
			fsize = meta['files'][fname]
			data = ''		
			buffsize = 128
			while 1:
				time.sleep(0.01)
				if fsize > buffsize:
					newData = soc.recv( buffsize )
				
					if len(newData) == 0:
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
	def jsonme( self ):
		data = {}
		data['objs'] = self.objs
		data['imname'] = self.img
		data['solved'] = self.solved
		data['timeout'] = self.timeout
		if self.tend:
			data['timer'] = self.tend-self.t0
		else:
			data['timer']=time.time()-self.t0

		return json.dumps(data, indent=2, sort_keys=True)

	
def addwcs( imgfd, wcsfd, imgext=0, wcsext=0 ):
	#add wcs and try to save in place
	for key, value in wcsfd[wcsext].header.iteritems():
		
		
		if key == "COMMENT":
			imgfd[imgext].header.add_comment( value )
			
		elif key == "HISTORY":
			imgfd[imgext].header.add_history( value )
		
		elif key in ['DATE', 'SIMPLE', 'NAXIS']:
		#dont replace these keys
			pass
			
		else:
		
			if key in imgfd[imgext].header:
				imgfd[imgext].header[key+'0'] = imgfd[imgext].header[key]
			
			
			if key != 'HISTORY':
				imgfd[imgext].header[key] = ( wcsfd[wcsext].header[key], "From astrometry.net" )
	
	

			
			
def main(img):
	fitsfd = fits.open( img, mode='update' )
	resp = solvefitsfd( fitsfd, port=9004 )
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

	hostname = 'jefftest2.as.arizona.edu'
	portnum = 9002
	timeout = 60.0
	
	parser = argparse.ArgumentParser(description='Slotis Image Solver Client.')
	parser.add_argument('--host', type=str , help='Host name or IP address of Image Server, default={}.'.format(hostname), default=hostname)
	parser.add_argument('--port', type=int, help='Port of Image Server, default={}.'.format(portnum), default=portnum)
	parser.add_argument('--radius', type=float, help='Search radius in Degrees of the solver.')
	parser.add_argument('--timeout', type=float, help='How long for the imclient to wait for solution from the server default={}.'.format(timeout), default=timeout)
	parser.add_argument('--log', type=str, help='Directory where logfiles will be placed. If absent no logging will be done', default=None )
	parser.add_argument('--thread-limit', type=int, metavar="thread_limit", help='Limit on how many threads will be run in parallel', default=5) 
	parser.add_argument('images', metavar='Fits Images', type=str, nargs='+', help='List of Slotis Fits images to be solved.')
	

	args = parser.parse_args()
	
	threads = []
	threadLimit = args.thread_limit
	
	for img in args.images:
		t0 = time.time()
		fd = fits.open(img)
		thisThread = solverThread( img, args.host, args.port, timeout=args.timeout, radius=args.radius )
		threads.append( thisThread )
	
	threads[0].start()
	
		
		
	nSolved, nLiveThreads, nNotSolved = checkThreads( threads )
	threadIndex = 1
	while threadIndex < len(threads):
		nSolved, nLiveThreads, nNotSolved = checkThreads( threads )
		if nLiveThreads < threadLimit:
			threads[ threadIndex ].start()
			threadIndex+=1
		else:
			print "Too many Threads. Waiting till one solves or fails. {} Threads running.".format(nLiveThreads)
			
		time.sleep(1.0)
				


	nSolved, nLiveThreads, nNotSolved = checkThreads( threads )
	t0 = time.time()
	while nLiveThreads > 0:
		now = time.time()
		nSolved, nLiveThreads, nNotSolved = checkThreads( threads )
		print "waiting for {} threads to finish, {:.1f}".format(nLiveThreads, now-t0)
		#Make sure the remaining threads don't take too long!
		if (now - t0) > args.timeout*nLiveThreads + 5:
			print "The last Threads took too long timing out."
			break
		
		time.sleep(1.0)
	print "All threads have finished."
	print "{} failed\n{} solved".format(nNotSolved, nSolved)

	
	print args.log
	if args.log:
		
		if args.log.endswith('/'):
			args.log = args.log[:-1]
		
		for thread in threads:
			fname = thread.img.replace( '.fits', '' )
			fname+='.json'
			fd = open("{}/{}".format(args.log, fname) , 'w')
			fd.write( thread.jsonme() )
			
			
			

