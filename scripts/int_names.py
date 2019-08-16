from requests_futures.sessions import FuturesSession
import config
import json
import requests

import sched, time
import datetime




def get_GNreversegeo_params(url,lat,lon,username):
    return  {'url': url, 
             'params': {'lat' : lat,
                        'lng' : lon,
                        'username' : username}}

def get_int_street_names(future):
    result = future.result()
    json_int = json.loads(result.text)
    try:
        return (json_int['intersection']['street1'], json_int['intersection']['street2'])
    except:
        return ('no_int_found','no_int_found')

def get_int_names(n,signal_list):
    
    url = 'http://api.geonames.org/findNearestIntersectionJSON'
    
    session = FuturesSession(max_workers=10)
    
    futures_lst = [session.get(**get_GNreversegeo_params(url, lat, lon, config.GEONAMES_acct)) 
               for lat, lon in signal_lat_lons[n:n+1000]]
    
    signal_name_lst = [[(signal_lat_lons[n+ix][0],signal_lat_lons[n+ix][1]), get_int_street_names(future)] 
                       for ix, future in enumerate(futures_lst)]
    
    signal_list.extend(signal_name_lst)
    
    print(n)
    
    return None

def save_file(sig_names):
    with open('signal_names.csv', 'w') as f:
        [f.write('{0},{1},{2},{3}\n'.format(lat,lon,st1,st2)) for (lat, lon), (st1, st2) in sig_names]
    return None


#Get traffic signal locations
file=open('NYC_traffic_signals.geojson','r')
traffic_signals_json = json.load(file)
file.close()

signal_lat_lons = [(node['geometry']['coordinates'][1], node['geometry']['coordinates'][0]) for node in traffic_signals_json['features']]

#Set up scheduler
s = sched.scheduler(time.time, time.sleep)

#Initialize signal names list
sig_names = [[('lat','lon'),('cross_street_1','cross_street_2')]]

print(datetime.datetime.now())

#Loop over get requests
for j in range(12):
    s.enter(j*3630, 1, get_int_names, (j*1000,sig_names))

#save to file
s.enter(60+11*3630, 1, save_file, (sig_names,))

s.run()
    