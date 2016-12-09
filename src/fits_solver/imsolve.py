#!/usr/bin/python

from astropy.io import fits
import sys
import os
import argparse
import json
import subprocess
import shlex
import collections
import re
from astro.angles import RA_angle, Dec_angle, Angle, Deg10



default_params = {
		'radius':5,
		'scale-units': 'app',
		'scale-low':0.2,
		'scale-high':1,
}

default_flags =  ['overwrite', 'crpix-center']

class imenc( json.JSONEncoder ):

	def default( self, obj ):
	
		return json.JSONEncoder.default(self, obj)

	
class mont4k( collections.MutableMapping ):
	info = {}
	default_params = {
		
		'scale-units': 'app',
		'scale-low':0.1,
		'scale-high':0.6,
	}
	
	default_flags =  ['overwrite', 'crpix-center']

	def __init__(self, imname, indir='.', outdir='astrometry'):
		
		self.imname = imname
		self.path = indir
		
		
		
		self.astropyimg = fits.open("{0}/{1}".format( indir, imname ) ) 
		if outdir != '.' and not os.path.exists( outdir ):
			os.mkdir(outdir)
		
		
		self.default_params['dir'] = outdir
		
		self.tcsra = self.astropyimg[0].header['ra']
		self.tcsdec = self.astropyimg[0].header['dec']
		
	def __delitem__(self, key):
		del self.info[key]
	
	def __iter__( self ):
		return iter( json.loads(self.__str__() ) )
	
	
	
	
	def __len__( self ):
		len(self.info)

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
		output = {}
		for key,val in self.info.iteritems():
			if isinstance( val, fits.hdu.hdulist.HDUList ):
				pass
			else:
				output[key] = val
		return json.dumps( output )
	
	
	def __dict__( self ):
		output = {}
		for key,val in self.info.iteritems():
			if isinstance( val, fits.hdu.hdulist.HDUList ):
				pass
			else:
				output[key] = val
		return output
	
	
	def solve_ext( self, extnum ):
		params = self.default_params
		
		params['6'] = extnum

		params['ra'] = self.tcsra
		params['dec'] = self.tcsdec
		params['o'] = "{0}_ext{1}".format( self.imname.replace('.fits', ''), extnum )
		
		
		cmd = astrometry_cmd("{0}/{1}".format( self.path, self.imname), params, self.default_flags)
		self.info['cmd_ext{0}'.format(extnum)] = cmd
		
		"""
		Field: /home/scott/data/flexdata/pointing0037.fits
		Field center: (RA,Dec) = (90.07, 13.31) deg.
		Field center: (RA H:M:S, Dec D:M:S) = (06:00:16.596, +13:18:24.830).
		Field size: 4.9711 x 9.67556 arcminutes
		Field rotation angle: up is 0.272245 degrees E of N
		"""
		
		
		
		resp = subprocess.check_output( shlex.split(cmd) )
		
		coords_finder = re.compile( "Field center: \(RA H:M:S, Dec D:M:S\) = \((\d\d:\d\d:\d\d\.\d?\d?\d), ([+|-]\d\d:\d\d:\d\d\.\d?\d?\d?)")
		#finder = re.compile("Field center: \(RA H:M:S, Dec D:M:S\) = \((\d\d:\d\:\d\d\.\d?\d?\d?), [+\-](\d\d:\d\d:\d\d\.\d?\d?\d?\)).")
		match = coords_finder.search(resp)
		
		if match:
			self.info['ra_ext{0}'.format(extnum)],self.info['dec_ext{0}'.format(extnum)] = match.group(1), match.group(2)
			
			return match.group(1), match.group(2)
			
		return False
		
		
	def solve_all(self):
		coords = []
		for extnum in range(1,len(self.astropyimg)):
			reply = self.solve_ext( extnum )
			if reply:
				ra, dec = RA_angle( reply[0]), Dec_angle(reply[1] )
				coords.append((ra,dec))
				
		
		
		
		
		
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



	return "/usr/local/astrometry/bin/solve-field {0} {1}".format( args, fname )
	#return "solve-field {0} {1}".format( args, fname )
	
	



def getazcamradec(fd):
	return (fd[0].header['ra'], fd[0].header['dec'])
	

def getfl50radec(fd):
	radra = fd[0].header['apra']
	raddec =  fd[0].header['apdec']

	ra, dec = (Angle(radra)), Angle(raddec)

	return(ra.Format("hours"), dec.Format("degarc180"))
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

		#astro_params['ra'], astro_params['dec'] = getazcamradec( img )
		astro_params['ra'], astro_params['dec'] = getfl50radec( img )

		
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


