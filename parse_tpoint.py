import json
from angles import Deg10, RA_angle, Dec_angle

def ascii_encode_dict(data):
    ascii_encode = lambda x: str(x).encode('ascii')
    return dict(map(ascii_encode, pair) for pair in data.items())

f=open("offsets.json", 'r')

outfile = open("tpoint_90.dat", 'w')
data = json.loads(f.read(), object_hook=ascii_encode_dict)

obsStr = "{0:02d} {1:02d} {2:02d}  {3:03d} {4:02d} {5:02d}"
calStr = "{0:02d} {1:02d} {2:02d}  {3:03d} {4:02d} {5:02d}"

lineStr = "{0}  {1}  {2}  {3}  {4}"

for datum in data:
	try:
		calRA, calDec = RA_angle( str(datum['midpointRA'] ) ), Dec_angle( str( datum['midpointDec'] ) )
		obsRA, obsDec = RA_angle( str( datum['obsRA'] ) ), Dec_angle( str( datum['obsDec'] ) )
		lst = RA_angle( datum['lst'] )
		#this prints the data for observation format record 1 in the tpoint manual in section 4.5.4 "Observation records"
		print lineStr.format( obsRA.Format('hours', ' ')[:-3], obsDec.Format('degarc180', ' ')[:-3], calRA.Format('hours', ' ')[:-3], calDec.Format('degarc180', ' ')[:-3], lst.Format('hours', ' ')[:-5] )

	except(Exception):
		print datum

	#print line.format( ra_hh=obsRA.hours[0], ra_mm=obsRA.hours[1], ra_ss=obsRA.hours[2], dec_dd=obs  )
	


outfile.close()