#!/usr/bin/python python
import sys
import os
import psycopg2
import urllib2
import time
#import zoo
#import episode
#import POP_EQ_wps
#import grass.script as grass
#import grass.script.setup as gsetup
#from shapely.wkt import loads
#from geojson import dumps

GISBASE = "/usr/lib/grass64/"

os.environ['GISBASE'] = GISBASE
os.environ['PATH'] = os.environ['PATH'] + ":$GISBASE/bin:$GISBASE/scripts"
if 'LD_LIBRARY_PATH' in os.environ.keys():
    os.environ['LD_LIBRARY_PATH'] = os.environ['LD_LIBRARY_PATH'] + ":$GISBASE/lib"
else:
    os.environ['LD_LIBRARY_PATH'] = "$GISBASE/lib"

# for parallel session management, we use process ID (PID) as lock file number:
os.environ['GIS_LOCK'] = str(os.getpid())
# path to GRASS settings file
os.environ['GISRC'] = "$HOME/.grasssrc6"

grasspath = os.path.join(GISBASE, 'etc','python')
if grasspath not in sys.path:
    sys.path.append(grasspath)

LOCATION = "tempdata"
GISDBASE = "/home/user/grassdata"
MAPSET = "PERMANENT"

from grass import script as gscript
from grass.script import setup
setup.init(GISBASE, GISDBASE, LOCATION, MAPSET)
#from grass.pygrass import vector
from grass.script import core as mg

# request service georss from haii
resp = urllib2.urlopen('http://localhost/xml/load_rain_json_tmd.php')
#loaddata = resp.read()
#print loaddata+"Download Finish!!"

def tempidw(conf,inputs,outputs):

	# Set path result rain idw method
	path = '/usr/local/lib/geoserver-2.5/data_dir/coverages/result_data/'
	#path = '/var/lib/tomcat6/webapps/geoserver/data/coverages/result_data/'
	#path2 = '/home/user/data/chai/rasters/'
	t = time.strftime("%Y%m%d:%H%M%S")
	print t+"=> Hello times!!"
	#connection = psycopg2.connect(dbname='rain', host='localhost', port='5432', user='user', password='##geonred2015##')
	
	# Import point rainfall data from PostgreSQL/PostGIS
	mg.run_command('v.in.ogr', dsn='PG:dbname=rain', layer='temp_tmd_f', output='temp_tmd_f', overwrite= True)
	
	# Set Extent and Interpolation IDW Method
	#mg.run_command('g.region', rast='rainthai_idw@PERMANENT',res='1000', quiet= True)
	mg.run_command('g.region', n='2263224.73894777', e='1213679.82470656', s='620826.97426737', w='325216.68257497', res='500')
	mg.run_command('v.surf.idw', input='temp_tmd_f@PERMANENT', output='tempidw', power='2.0', column='temperatur',flags='n', overwrite= True)
	
	# Genarate Contour line (isolines)
	#mg.run_command('r.contour', input='rainthai_idw@PERMANENT', output='rain_isoline', step='5', overwrite= True)
	
	# Export rain_idw gdal to GeoTiff file and timestamp
	mg.run_command('r.out.gdal', input='tempidw@PERMANENT', type='Float64', output= path+'tempidw_'+t+'.tif') #, overwrite= True
	mg.run_command('r.out.gdal', input='tempidw@PERMANENT', type='Float64', output= path+'tempidw.tif', overwrite= True)
	
	# test
	#mg.run_command('r.out.gdal', input='rainthai_idw@PERMANENT', type='Float64', output= path2+'rain_idw2.tif', overwrite= True)
	
	# remove rast
	#mg.run_command('g.remove', rast='rainthai_idw@PERMANENT',quiet= True)
	
	# Export Contour line into PostgreSQL/PostGIS
	#v.out.ogr input=rain_isoline@PERMANENT type=line dsn=PG:host=localhost dbname=rain user=user olayer=rain_isoline format=PostgreSQL
	#mg.run_command('v.out.ogr', input='rain_isoline@PERMANENT', type='line', dsn='PG:dbname=rain', olayer='rain_isoline', format='PostgreSQL',overwrite= True) #,flags='u'
		
	#mg.run_command('v.delaunay', input='archsites',output='test_delaunay') 
	
	# Create Voronoi from Rain Station
	#v.voronoi input=rainthai_f@PERMANENT output=rain_voronoi --overwrite
	#mg.run_command('v.voronoi', input='rainthai_f@PERMANENT',output='rain_voronoi', overwrite= True) 
	
	#mg.run_command('v.out.ogr', input='rain_voronoi@PERMANENT', type='area', dsn='PG:dbname=rain', olayer='rain_voronoi', format='PostgreSQL',overwrite= True) #,flags='u'
	
	
	outputs["Result"]["value"]="Hello "+inputs["a"] ["value"]+" your processing is completed!!!!!!"
	
	return 3
