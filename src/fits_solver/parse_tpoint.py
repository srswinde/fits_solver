import json
from astro.angles import Deg10, RA_angle, Dec_angle
import sys
def ascii_encode_dict(data):
    ascii_encode = lambda x: str(x).encode('ascii')
    return dict(map(ascii_encode, pair) for pair in data.items())


if len(sys.argv) > 1: 
	f=open(sys.argv[1], 'r')
else:
	f=open("astrometry.json", 'r')

data = json.loads(f.read(), object_hook=ascii_encode_dict)

obsStr = "{0:02d} {1:02d} {2:02d}  {3:03d} {4:02d} {5:02d}"
calStr = "{0:02d} {1:02d} {2:02d}  {3:03d} {4:02d} {5:02d}"

lineStr = "{0}  {1}  {2}  {3}  {4}"

for datum in data:
	try:
		calRA, calDec = RA_angle( str(datum['midpointRA'] ) ), Dec_angle( str( datum['midpointDec'] ) )
		obsRA, obsDec = RA_angle( str( datum['obsRA'] ) ), Dec_angle( str( datum['obsDec'] ) )
		lst = RA_angle( datum['lst'] )
		lststr = "{0:02d} {1:04.2f}".format(lst.hours[0], lst.hours[1]+lst.hours[2]/60.0)
		#this prints the data for observation format record 1 in the tpoint manual in section 4.5.4 "Observation records"
		print lineStr.format( calRA.Format('hours', ' ')[:-3], calDec.Format('degarc180', ' ')[:-3], obsRA.Format('hours', ' ')[:-3], obsDec.Format('degarc180', ' ')[:-3], lststr)

	except ValueError as err:
		
		print err

	#print line.format( ra_hh=obsRA.hours[0], ra_mm=obsRA.hours[1], ra_ss=obsRA.hours[2], dec_dd=obs  )
	


