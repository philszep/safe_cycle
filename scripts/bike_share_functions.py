import pandas as pd
import numpy as np

def bike_clean_df(df, subs_only = True, cust_only=False,max_tripdur= 2):
    """Cleans bikeshare dataframe. 
    Removes NaN
    Filter out non-subscribers (if subs_only = True)
    Filter out subscribers (if subs_only = False and cust_only = True)
    Drops trips longer than max_tripdur (in hours)
    Converts station ids to ints
    Converts datetime strings to datetime objects
    """

    len_df = len(df)
    #Drop NaN values
    df.dropna(inplace=True)
    print('Dropped {} NaN entries'.format(len_df-len(df)))


    #Restrict to subscribers    
    if subs_only:
        print('Keeping only subscribers')
        clean_df = df[df['usertype'] == 'Subscriber'].copy() # Careful with copy when DF contains mutable objects like lists....
        
        print('Dropped an additional {} non-subscriber entries'.format(len(df)-len(clean_df)))
    
    elif cust_only:
    #Restrict to subscribers   
        print('Keeping only Customers') 
        clean_df = df[df['usertype'] == 'Customer'].copy() # Careful with copy when DF contains mutable objects like lists....
        print('Dropped {} subscriber entries'.format(len(df)-len(clean_df)))
    else:
        clean_df = df
    
    clean_df.loc[clean_df['usertype'] =='Customer','usertype'] = 0
    clean_df.loc[clean_df['usertype'] =='Subscriber','usertype'] = 1

    len_clean_df = len(clean_df)
    #Drop trips longer than two hours
    clean_df = clean_df[clean_df['tripduration'] < max_tripdur*3600]
    print('Dropped an additional {} entries with trips longer than {} hours'.format(len_clean_df-len(clean_df),max_tripdur))

    #Convert station ids to integers
    clean_df.loc[:,'start station id']=clean_df['start station id'].astype(int,copy=False)
    clean_df.loc[:,'end station id']=clean_df['end station id'].astype(int,copy=False)
    print('Changed type of start station id and end station id to integer')

    #Convert to datetime
    clean_df['starttime'] = pd.to_datetime(clean_df['starttime'])
    clean_df['stoptime'] = pd.to_datetime(clean_df['stoptime'])
    print('Changed type of starttime and stoptime to datetime')

    len_clean_df = len(clean_df)

    #Remove start stations outside of NYC
    
    clean_df.drop(clean_df[clean_df['start station latitude'] > 41].index,inplace=True)
    clean_df.drop(clean_df[clean_df['start station latitude'] < 40].index,inplace=True)
    clean_df.drop(clean_df[clean_df['start station longitude']>-73.8].index,inplace=True)
    clean_df.drop(clean_df[clean_df['start station longitude']<-74.1].index,inplace=True)

    #Remove end stations outside of NYC
    clean_df.drop(clean_df[clean_df['end station latitude'] > 41].index,inplace=True)
    clean_df.drop(clean_df[clean_df['end station latitude'] < 40].index,inplace=True)
    clean_df.drop(clean_df[clean_df['end station longitude']>73.8].index,inplace=True)
    clean_df.drop(clean_df[clean_df['end station longitude']<-74.1].index,inplace=True)

    print('Dropped an additional {} trips with start/end stations outside NYC'.format(len_clean_df - len(clean_df)))

    return clean_df
    

def get_trip_info(df):
    """Extracts some relevant data from trips
    Drops cols: ['start station name', 'start station latitude', 'start station longitude', 'end station name', 'end station latitude', 'end station longitude']
    Adds cols: ['start_day', 'stop_day','pickup_hour','dropoff_hour', 'age', Trip_Type','start_end_station']
    """
    trip_info_df = df.copy() #Careful with .copy() of dataframe if entries include lists!
 
    trip_info_df.drop(columns = ['usertype','start station name', 'start station latitude', 'start station longitude', 'end station name', 'end station latitude', 'end station longitude'],inplace=True)

    
    #Get weekday labels and create column
    trip_info_df['start_day'] = trip_info_df['starttime'].map(lambda x: x.weekday()) # 0 = Monday, .. , 6 = Sunday
    trip_info_df['stop_day'] = trip_info_df['stoptime'].map(lambda x: x.weekday()) # 0 = Monday, .. , 6 = Sunday

    #Get hours and create column
    trip_info_df['pickup_hour'] = trip_info_df['starttime'].map(lambda x: x.hour) # 0 .. 24
    trip_info_df['dropoff_hour'] = trip_info_df['stoptime'].map(lambda x: x.hour) # 0 .. 24

    #Get age
    trip_info_df['age'] = 2018 - trip_info_df['birth year']


    #Assign different times to types of trip 
    #Weekend = [Sat,Sun], 'Late Night' = before 6am or after 8pm, 'Commuter' = 6-10am or 4-8pm, 'Daytime Errand' = 10am-4pm)
    trip_info_df = trip_info_df.assign(Trip_Type =
    np.select(
        condlist=[trip_info_df['start_day'] == 5, trip_info_df['start_day']==6, trip_info_df['pickup_hour'] < 6, trip_info_df['pickup_hour'] <10, trip_info_df['pickup_hour'] < 16, trip_info_df['pickup_hour']<20, trip_info_df['pickup_hour'] < 24], 
        choicelist=['Weekend','Weekend','Late Night','Commuter','Midday','Commuter','Late Night'], 
        default='Other'))

    #Create column of start-end station pairs
    trip_info_df = trip_info_df.assign( start_end_station = tuple(zip(trip_info_df.loc[:,'start station id'], trip_info_df.loc[:,'end station id'])))

    # Remove ordering (forget which station is start/end)
    #start_end = subs_df['start_end_station'].copy()
    trip_info_df['start_end_station'] = trip_info_df['start_end_station'].map(lambda x: tuple(sorted(x)))


    return trip_info_df



def get_stations_info(df, city = 'NYC'):
    """ Create station info dataframe from bike share dataframe.
        df: bikeshare dataframe
        Return: dataframe with index = 'station_id' and columns = ['station_name', 'lon','lat']
    """
    if city == 'NYC':
        st_stations_info_df = df[['start station id','start station latitude', 'start station longitude','start station name']].set_index('start station id')
        st_stations_info_df = st_stations_info_df.drop_duplicates()
        st_stations_info_df.rename({'start station name': 'station name','start station longitude': 'lon', 'start station latitude': 'lat'},axis=1,inplace=True)

        end_stations_info_df = df[['end station id','end station latitude', 'end station longitude','end station name']].set_index('end station id')
        end_stations_info_df = end_stations_info_df.drop_duplicates()
        end_stations_info_df.rename({'end station name': 'station name','end station longitude': 'lon', 'end station latitude': 'lat'},axis=1,inplace=True)

        stations_info_df = pd.concat([st_stations_info_df,end_stations_info_df],axis = 0)
        stations_info_df.drop_duplicates(inplace=True)

        #Remove stations outside of NYC (in case they haven't already been removed)
        drops=stations_info_df[stations_info_df['lat']>41].index
        stations_info_df.drop(drops,inplace=True)

        lat_Max_df = stations_info_df[stations_info_df['lat']<41]
        lat_Min_df = stations_info_df[stations_info_df['lat']>40]
        lon_Max_df = stations_info_df[stations_info_df['lon']<-73.8]
        lon_Min_df = stations_info_df[stations_info_df['lon']>-74.1]
        stations_info_df = pd.concat([lat_Max_df,lat_Min_df,lon_Max_df,lon_Min_df],axis=0).drop_duplicates()
        stations_info_df.rename_axis('station_id',inplace=True)

    return stations_info_df

# Below is another way of creating the stations_info_df, there were issues here because only 
# currently active stations are included in station_information.json and this does not include 
# those on Governors Island 

# Build the NYC station info df (with lat, long, name, capacity)
# This station file seems to be missing at least one station (id = 3254) figure this out later, for now us stations_info_df 
# Extracted from the data itself...
#stations_file = open('./data/NYC/station_information.json','r')
#stations = stations_file.read()
#stations_file.close()

#stations_json = json.loads(stations)
#stations_json_list = stations_json['data']['stations']
#stations_json_list = stations_json['stationBeanList']


#stations_info_df = pd.DataFrame(stations_json_list)
#stations_info_df.drop(['has_kiosk','region_id','rental_methods','rental_url','short_name','eightd_has_key_dispenser','eightd_station_services','electric_bike_surcharge_waiver','external_id'],axis = 1,inplace=True)
#stations_info_df['station_id'] = stations_info_df['station_id'].astype('int')
#stations_info_df[stations_info_df['name'] == ' Soissons Landing']

#stations_info_df.set_index('station_id',inplace=True)
#stations_info_df[stations_info_df['station_id']==3264]
#stations_info_df.drop(['city','is_renting', 'availableDocks','availableBikes','altitude','landMark','lastCommunicationTime','postalCode','location','stAddress2','status','statusValue','statusKey','testStation','stAddress1','kioskType'],axis = 1,inplace=True)   
#stations_info_df.set_index('id',inplace=True)
#stations_info_df


def get_hourly_pickups(df, weekday_only = False, weekend_only = False):
    """ Create dataframe of number of pick_ups per station per hour
    """
    #Create weekday and weekend dataframes
    if weekday_only == True:
        pickup_df = df[df['Trip_Type'] != 'Weekend'].copy()
    elif weekend_only == True:
        pickup_df = df[df['Trip_Type'] == 'Weekend'].copy()
    else:
        pickup_df  = df.copy()


    return pickup_df