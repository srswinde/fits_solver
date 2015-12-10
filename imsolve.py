#!/usr/bin/python

from astropy.io import fits
import sys
import os

def do_astrometry(fname, params={}, flags=[]):
	args = ''
	for name, val in params.iteritems():
		print name
		if len(name) == 1:
			args+=" -{0} {1} ".format(name, val)
		else:
			args+=" --{0} {1} ".format(name, val)

	for flag in flags:
		print flag
		if len(flag) == 1:
			args+=" -{0} ".format(flag)
		else:
			args+=" --{0} ".format(flag)



	return "solve-field {0} {1}".format( args, fname )
	
if len(sys.argv) < 2:
	print "idiot"

	sys.exit()

if  not os.path.exists('anal'):
	
	os.mkdir('anal')
	
for num in range(12,130):
	#fname = sys.argv[1]
	fname = "pointing{0:04d}.fits".format(num)
	print fname
	fd = fits.open(fname)

	p={

		'ra':fd[0].header['ra'],
		'dec':fd[0].header['dec'],
		'radius':5,
		'scale-units': 'app',
		'scale-low':0.1,
		'scale-high':2,
		'6':2,
		'dir':'anal'
	
	}



	cmd = do_astrometry(fname, p, ['overwrite', 'crpix-center'])
	print cmd

	os.system(cmd)
