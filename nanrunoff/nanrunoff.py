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

LOCATION = "nanrunoff"
GISDBASE = "/home/user/grassdata"
MAPSET = "PERMANENT"

from grass import script as gscript
from grass.script import setup
setup.init(GISBASE, GISDBASE, LOCATION, MAPSET)
#from grass.pygrass import vector
from grass.script import core as mg

# request service georss from haii
resp = urllib2.urlopen('http://localhost/dl/nanrunf/haiidata.php')
#loaddata = resp.read()
#print loaddata+"Download Finish!!"

def nanrunoff(conf,inputs,outputs):

	# Set path result rain idw method
	path = '/var/www/html/dl/data/nanrainfall/'
	#path = '/usr/local/lib/geoserver-2.5/data_dir/coverages/result_data/'
	#path = '/var/lib/tomcat6/webapps/geoserver/data/coverages/result_data/'
	#path2 = '/home/user/data/chai/rasters/'
	t = time.strftime("%Y%m%d:%H%M%S")
	print t+"=> Hello times it work[200]!"
	connection = psycopg2.connect(dbname='nanrunf', host='localhost', port='5432', user='user', password='user')
	
	# Import point rainfall data from PostgreSQL/PostGIS
	mg.run_command('v.in.ogr', dsn='PG:dbname=nanrunf', layer='nan_raingrass', output='nan_raingrass', overwrite= True)
	
	# Set Extent and Interpolation IDW Method
	#mg.run_command('g.region', rast='rainthai_idw@PERMANENT',res='1000', quiet= True)
	mg.run_command('g.region', n='2172120.86468637', e='748094.237955', s='1735854.76591878', w='558440.48801759', res='40')
	mg.run_command('v.surf.idw', input='nan_raingrass@PERMANENT', output='nan_idw', power='2', column='rain',flags='n', overwrite= True)
	#mg.run_command('v.surf.idw', input=inputs["idw_vect"] ["value"], output=inputs["idw_rast"] ["value"], power='2', column='rain',flags='n', overwrite= True)
	#mg.run_command('v.surf.idw', input=inputs["idw_vect"] ["value"], output=inputs["idw_rast"] ["value"], power=inputs["idw_power"] ["value"], column=inputs["idw_column"] ["value"],flags='n', overwrite= True)
	
	# Genarate Contour line (isolines)
	#mg.run_command('r.contour', input='rainthai_idw@PERMANENT', output='rain_isoline', step='5', overwrite= True)
	
	# Export rain_idw gdal to GeoTiff file and timestamp
	#mg.run_command('r.out.gdal', input='nan_idw@PERMANENT', type='Float64', output= path+'nanrainf_'+t+'.tif') #, overwrite= True
	#mg.run_command('r.out.gdal', input=inputs["idw_rast"] ["value"], type='Float64', output= inputs["dsn_export"] ["value"]+'_nanrain_'+t+'.tif') #, overwrite= True
	#mg.run_command('r.out.gdal', input='nan_idw@PERMANENT', type='Float64', output= path+'nanrainf.tif', overwrite= True)
	#mg.run_command('r.out.gdal', input='nan_idw@PERMANENT', type='Float64', output= path+'nanrainf_'+t+'.tif') #, overwrite= True
	
	# test mapcal runoff nanbasin
	# r.mapcalc nrunoff = ( pow( ( nan_idw@PERMANENT - ( 0.2 * grid_s@PERMANENT ) )  ,2 ) ) / ( nan_idw@PERMANENT + ( 0.8 * grid_s@PERMANENT ) )
	mg.write_command('r.mapcalc', stdin= 'nrunoff = ( pow( ( nan_idw@PERMANENT - ( 0.2 * grid_s@PERMANENT ) )  ,2 ) ) / ( nan_idw@PERMANENT + ( 0.8 * grid_s@PERMANENT ) )')
	
	mg.write_command('r.mapcalc', stdin= 'nrunoff_sqm3rai = (nrunoff@PERMANENT/1000)*1600')
	# to raster runoff output
	#mg.run_command('r.out.gdal', input=inputs["nrunoff"] ["value"], type='Float64', output= inputs["dsn_export"] ["value"]+'_runoff_'+t+'.tif') #, overwrite= True
	mg.run_command('r.out.gdal', input='nrunoff_sqm3rai@PERMANENT', type='Float64', output= path+'nanrunoff.tif', overwrite= True)
	
	# to vector
	#mg.run_command('r.to.vect', input='raincal@PERMANENT', output='warnings', feature='area', overwrite= True)
	
	
	# remove rast
	#mg.run_command('g.remove', rast='rainthai_idw@PERMANENT',quiet= True)
	
	#connection = psycopg2.connect(dbname='nanrunf', host='localhost', port='5432', user='user', password='user')
	#res = connection.cursor()
	#res.execute("DROP VIEW IF EXISTS _villrisk ;")
	#res.execute("DROP VIEW IF EXISTS vill_warn ;")
	#res.execute("DROP TABLE IF EXISTS warnings ;")
	#connection.commit()
	
	# Export warnning areas into PostgreSQL/PostGIS
	#v.out.ogr input=rain_isoline@PERMANENT type=line dsn=PG:host=localhost dbname=rain user=user olayer=rain_isoline format=PostgreSQL
	#mg.run_command('v.out.ogr', input='warnings@PERMANENT', type='area', dsn='PG:dbname=nanrunf', olayer='warnings', format='PostgreSQL',overwrite= True) #,flags='u',lco="OVERWRITE=YES"
	#mg.run_command('v.out.ogr', input='warnings@PERMANENT', type='area', flags='c', dsn='PG:host=localhost dbname=nanrunf user=user password=user', olayer='warnings', format='PostgreSQL')	
	
	#mg.run_command('v.delaunay', input='archsites',output='test_delaunay') 
	
	# Create Voronoi from Rain Station
	#v.voronoi input=rainthai_f@PERMANENT output=rain_voronoi --overwrite
	#mg.run_command('v.voronoi', input='rainthai_f@PERMANENT',output='rain_voronoi', overwrite= True) 
	
	#mg.run_command('v.out.ogr', input='rain_voronoi@PERMANENT', type='area', dsn='PG:dbname=rain', olayer='rain_voronoi', format='PostgreSQL',overwrite= True) #,flags='u'
	
# 	connection = psycopg2.connect(dbname='nanrunf', host='localhost', port='5432', user='user', password='user')
# 	res = connection.cursor()
# 	res.execute("DROP VIEW IF EXISTS _villrisk ;")
# 	res.execute("DROP VIEW IF EXISTS vill_warn ;")
# 	res.execute("DROP TABLE IF EXISTS warnings ;")
# 	res.execute("CREATE VIEW vill_warn AS SELECT v.gid, v.vill_code, v.vill_nam_t, v.geom FROM village_nbasin v, warnings w WHERE ST_Within (v.geom,w.wkb_geometry);")
# 	res.execute("CREATE VIEW _villrisk AS SELECT vw.gid, vw.vill_code, vw.vill_nam_t, vw.geom FROM vill_warn vw, landslide ls WHERE ST_Within (vw.geom,ls.geom);")
# 	connection.commit()
	
	outputs["Result"]["value"]=\
	"--> start process by: "+inputs["name"] ["value"]+ " --> Nan runoff processing successfully"
	
	return 3
