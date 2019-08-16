import pandas as pd
import sqlite3
import re

from bike_share_functions import bike_clean_df, get_stations_info, get_trip_info

conn = sqlite3.connect('NYC_bikes_2018.sqlite')
cur = conn.cursor()

#Clear tables if they exist
cur.execute('DROP TABLE IF EXISTS trips')
cur.execute('DROP TABLE IF EXISTS stations')
cur.execute('DROP TABLE IF EXISTS old_stations')
cur.execute('DROP TABLE IF EXISTS usertypes')

#Creating usertypes table
cur.execute('CREATE TABLE usertypes (ID INTEGER PRIMARY KEY NOT NULL, usertype TEXT)')
cur.execute('''INSERT INTO usertypes (ID, usertype) 
                VALUES (0, 'customer'), (1, 'subscriber')''')
conn.commit()

#Initialize stations dataframe list 
stations_df_lst = []

#Read in trip info for 2018 and populate SQL trip table
for el in ['01','02','03','04','05','06','07','08','09','10','11','12']:
    
    print('Reading {}'.format(el))
    df = pd.read_csv('../data/2018/2018{}-citibike-tripdata/2018{}-citibike-tripdata.csv'.format(el,el))
    df = bike_clean_df(df, subs_only = False)
    print('Creating {} entry in stations_df_lst'.format(el))
    stations_df_lst.append(get_stations_info(df))

    print('Storing {} in trips table'.format(el))
    columns = df.columns 
    columns = [col.replace(' ', '_') for col in columns]
    df.columns = columns #Remove spaces from column names
    df[['tripduration','starttime','stoptime','start_station_id','end_station_id','bikeid','usertype','birth_year','gender']].to_sql(name='trips',con=conn,if_exists="append",index=False)

#Take station info and put into station SQL table (Need to clean this more by hand, some stations are still duplicated)
stations_df = pd.concat(stations_df_lst,axis=0).drop_duplicates()
columns = stations_df.columns 
columns = [col.replace(' ', '_') for col in columns]
stations_df.columns = columns
stations_df.to_sql(name ='stations',con=conn) #index of stations_df is station ID number, use this as PRIMARY KEY for station table

cur.close()
conn.close()