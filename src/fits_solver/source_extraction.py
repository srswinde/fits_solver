import numpy as np
import sep
from astropy.io import fits

import math
from astro.angles import RA_angle, Dec_angle
import tempfile


lookup = (
	'thresh', #* ``thresh`` (float) Threshold at object location.
	'npix',  #* ``npix`` (int) Number of pixels belonging to the object.
	'tnpix',	#* ``tnpix`` (int) Number of pixels above threshold (unconvolved data).
	'xmin',	#* ``xmin``, ``xmax`` (int) Minimum, maximum x coordinates of pixels.
	'xmax',
	'ymin',	#* ``ymin``, ``ymax`` (int) Minimum, maximum y coordinates of pixels.
	'ymax',
	'x',		#* ``x``, ``y`` (float) object barycenter (first moments).
	'y',
	'x2',		#* ``x2``, ``y2``, ``xy`` (float) Second moments.
	'y2',
	'xy',
	'a',		#* ``a``, ``b``, ``theta`` (float) Ellipse parameters.
	'b',
	'theta',
	'cxx',	#* ``cxx``, ``cyy``, ``cxy`` (float) Alternative ellipse parameters.
	'cyy',
	'cxy',
	'cflux',	#* ``cflux`` (float) Sum of member pixels in convolved data.
	'flux',	#* ``flux`` (float) Sum of member pixels in unconvolved data.
	'cpeak', #* ``cpeak`` (float) Peak value in convolved data.
	'peak',	#* ``peak`` (float) Peak value in unconvolved data.
	'xcpeak',	#* ``xcpeak``, ``ycpeak`` (int) Coordinate of convolved peak pixel.
	'ycpeak',
	'xpeak',	#* ``xpeak``, ``ypeak`` (int) Coordinate of convolved peak pixel.
	'ypeak',
	'flag'	#* ``flag`` (int) Extraction flags.
)

def getobjects( data, thresh=5.0 ):
	if data.dtype is not 'float32':
		data = np.array(data, dtype="float32")

	bkg = sep.Background(data)
	bkg = sep.Background(data, bw=64, bh=64, fw=3, fh=3)

	back = bkg.back()

	rms = bkg.rms()
	bkg.subfrom(data)
	thresh = thresh * bkg.globalrms
	objects = sep.extract(data, thresh)

	#print "there are ", len(objects), "objects"
	return objects


def mkfitstable( objects ):
	cols=[]
	for name in ('x', 'y'):
		cols.append( fits.Column(name=name, format='E', array=objects[name] ) )

	fwhms = 2*np.sqrt(math.log(2)*(objects['a']**2 + objects['b']**2))
	cols.append( fits.Column( name='fwhm', format='E', array=fwhms ) )
	coldefs = fits.ColDefs( cols )

	dtable = fits.BinTableHDU.from_columns( coldefs )

	return dtable

def listify(objects):
	cols=[]
	fwhms = 2*np.sqrt(math.log(2)*(objects['a'] + objects['b']))
	outlist = []
	for ii in range( len( fwhms ) ):
		outlist.append({ 'x':objects['x'][ii], 'y':objects['y'][ii], 'fwhm':fwhms[ii] })
	return outlist

def writetmpfits( img, extnum=2,  **tblargs ):

	if type(img) == str:
		img = fits.open( img )
	#ra,dec = img[0].header['ra'] , img[0].header['dec']


	tbhdu = mkfitstable( getobjects( img[extnum].data ) )


	
	for key, val in list(tblargs.items()):

		tbhdu.header[key] = val

	tname = "{0}.fits".format( tempfile.mktemp() )
	tbhdu.writeto(tname)
	del tbhdu
	img.close()
	return tname




