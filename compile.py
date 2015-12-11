from astropy.io import fits
from astro.angles import RA_angle, Dec_angle, Deg10
import os
import json
import argparse


example = {
		  "amp11Dec": "+85:05:02.77",
        "amp11RA": "08:21:46.83",
        "amp6Dec": "+84:34:01.54",
        "amp6RA": "08:58:31.27",
        "lst": "04:10:20",
        "midpointDec": "+84:49:32.15",
        "midpointRA": "08:40:09.05",
        "name": "pr0002",
        "obsDec": "+84:59:59.90",
        "obsHA": "-04:33:53",
        "obsRA": "08:41:13.24",
        "offsetDec": 359.82562633352575,
        "offsetRA": 359.7325301822657
}





def get_info():
	for name in ext1names:
		if name in os.listdir('ext2'):
			bname = name[:-4]
			ext1 = fits.open( 'ext1/{0}'.format(name) )
			ext2 = fits.open( 'ext2/{0}'.format(name) )
		
			d1 = fits.open( 'ext1/{0}.new'.format(bname) )

			dec = ext1[0].header['crval2']+(ext1[0].header['crval2']- ext2[0].header['crval2'])/2.0
			ra = ext1[0].header['crval1']+(ext1[0].header['crval1']- ext2[0].header['crval1'])/2.0
		
			ra = RA_angle( Deg10( ra ) )
			dec = Dec_angle( Deg10( dec ) )
	
			obsRA = d1[0].header['ra']
			obsDec =  d1[0].header['dec']
			obsHA =  d1[0].header['ha']
			obsLST = d1[0].header['lst-obs']

			info = {
				"obsDec"			: 	obsDec,
				"obsHA"			: 	obsHA,
				"obsRA"			: 	obsRA,
				'lst'				:	obsLST,
				'name'			:	bname,
				'midpointDec'	:	str(dec),
				'midpointRA'	:	str(ra),
			
			}
			infolist.append(info)

			
		
	json.dump( infolist, open('data.json','w'), sort_keys=True, indent=4 )



if __name__ == '__main__':
	parser = argparse.ArgumentParser(
	description=
"""compile.py:
This is a quick and dirty way to gather astrometric data from astrometry.net style solutions 
and make that information available for a

	Auther	:	Scott Swindell
	Date		:	12 10 2015"""
	)
	

	parser.add_argument('-o',  default='tpoint.json', help='output json file')

	

	parser.add_argument( 'path',  help='Directory of the solution files' )
	

	args = parser.parse_args()
	
	files = os.listdir( args.path )
	for fname in files:
		if fname[-3:] == 'wcs':
			






