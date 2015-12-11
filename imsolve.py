#!/usr/bin/python

from astropy.io import fits
import sys
import os
import argparse


default_params = {
		'radius':5,
		'scale-units': 'app',
		'scale-low':0.1,
		'scale-high':2,
}

default_flags =  ['overwrite', 'crpix-center']

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


