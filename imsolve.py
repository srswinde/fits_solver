#!/usr/bin/python

from astropy.io import fits
import sys
import os
import argparse
import json
import subprocess
import shlex

default_params = {
		'radius':5,
		'scale-units': 'app',
		'scale-low':0.1,
		'scale-high':2,
}

default_flags =  ['overwrite', 'crpix-center']

class imenc( json.JSONEncoder ):

	def default( self, obj ):
		print type(obj)
		
		if isinstance( obj, fits.hdu.image.PrimaryHDU ):
			#print obj.fileinfo[0]['filename']
			return 'foo'
		elif isinstance( obj, fits.hdu.image.ImageHDU ):
			return False
			
		else:
			json.JSONEncoder.default(self, obj)
		
	
class mont4k(  ):
	info = {}
	default_params = {
		'radius':5,
		'scale-units': 'app',
		'scale-low':0.1,
		'scale-high':0.6,
	}
	
	default_flags =  ['overwrite', 'crpix-center']
	tits = 'shit'
	def __init__(self, imname):
		
		self.imname = imname
		self.astropyimg = fits.open(imname) 
		
		
		self.tcsra = self.astropyimg[0].header['ra']
		self.tcsdec = self.astropyimg[0].header['dec']
		
		

	def __setitem__(self, key, val):
		if key != 'info':
			self.info[key] = val
	
	
	def __getitem__(self, key):
		
		if key != 'info':
		
			try:
				return self.info[key]
			except KeyError:
				return None
		
		return None
		
		
	def __setattr__(self, key, val ):
		if key != 'info':
			self.__setitem__( key, val )
	
	
	def __getattr__(self, key):
		return self.__getitem__( key )
	
	
	
	
	def __str__( self ):

		return json.dumps( self.info, indent=4, cls=imenc )
		
	
	def solve_ext( extnum ):
		params = defualt_params
		params['-6'] = extnum
		tcsra, tcsdec = self.astropyimg
		params['ra'] = self.tcsra
		params['dec'] = self.tcsdec
		print astrometry_cmd(params, default_flags)
		
		
	def solve_all(self):
	
		
		cmd = astrometry_cmd( self.imname, self.default_params, self.default_flags )
		print cmd
		print
		print
		print 
		s=subprocess.check_output(shlex.split(cmd))
		return s
		
		
		
def astrometry_cmd(fname, params={}, flags=[]):

	
	args = ''
	
	for name, val in params.iteritems():

		if len(name) == 1:
			args+=" -{0} {1} ".format(name, val)
		else:
			args+=" --{0} {1} ".format(name, val)

	for flag in flags:
		
		if len(flag) == 1:
			args+=" -{0} ".format(flag)
		else:
			args+=" --{0} ".format(flag)



	return "solve-field {0} {1}".format( args, fname )
	
	



def getazcamradec(fd):
	return (fd[0].header['ra'], fd[0].header['dec'])
	

	
	
if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(
	description=
"""imsolve.py:
This a barebones wrapper for astrometry.net. It has a few usefull parameters
hard coded and it knows how to get the ra and dec from the azcam style headers
that we are all used to.

	Auther	:	Scott Swindell
	Date		:	12 10 2015"""
	)
	

	parser.add_argument('-o',  default='astrometry', help='Output directory for the solution files.')
	parser.add_argument( '-e', type=int, default=-1, help='Which extension to solve default is all' )                  


	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-f', default=None,  help='fits file to solve')
	group.add_argument( '-d',  default=None, help='Directory of data. All fits files will be solved' )
	

	args = parser.parse_args()
	
	astro_params = default_params
	astro_flags = default_flags
	
	if  not os.path.exists(args.o):
	
		os.mkdir(args.o)
	astro_params['dir'] = args.o
		
	if args.f:
		bname = args.f.split( '/' )[-1]
		if '.fits' == bname[-5:]:
			bname = bname[:-5]
			
		img = fits.open(args.f)
		
		astro_params['ra'], astro_params['dec'] = getazcamradec( img )
		

		
		if args.e < 0:
			exts = range( 1, len(img) )
		else:
			exts = [args.e]
			
		for ext in exts:
			astro_params['6'] = ext
			astro_params['o'] = "{0}_ext{1}".format( bname, ext )
			cmd = astrometry_cmd( args.f, astro_params, astro_flags )
			print cmd
			
			os.system(cmd)
	
	else:
		
		fnames = os.listdir( args.d )
		for fname in fnames:
			
			if '.fits' == fname[-5:]:
				bname = fname[:-5]
			path_file = "{0}/{1}".format( args.d, fname )
			img = fits.open( path_file )
			astro_params['ra'], astro_params['dec'] = getazcamradec( img )	
			
			if args.e < 0:
				exts = range( 1, len(img) )
			else:
				exts = [args.e]
				
			
			for ext in exts:
				astro_params['6'] = ext
				astro_params['o'] = "{0}_ext{1}".format( bname, ext )
				cmd = astrometry_cmd( path_file, astro_params, astro_flags )
				print cmd
			
				os.system(cmd)


