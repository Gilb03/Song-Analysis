#MODULE IMPORTS 
import json
import spotipy 
import requests 
import datetime
import pandas as pd
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials



#OAUTH & PARAMS
client_id = 'client_id'
client_secret = 'client_secret'
username = 'username'
scope = 'scope'
redirect_uri = 'https://developer.spotify.com/dashboard/applications/495c67c3aa8041ffaf6377a055f9afea'
token = util.prompt_for_user_token(username=username, 
                                   scope=scope, 
                                   client_id=client_id,   
                                   client_secret=client_secret,
                                   redirect_uri = redirect_uri)


search = 'entertainment'
endpoint_url = 'https://api.spotify.com/v1/search?'

id_list = []
name_list = []
desc_list = []

type = 'show'    
market  = 'US'
limit = 50                                             
offset = 0  

more_runs = 1                                          
counter = 0  

                                                            
while((offset <= 1950) & (counter <= more_runs)):           



    query = f'{endpoint_url}'
    query += f'&q={search}'
    query += f'&type={type}'
    query += f'&offset={offset}'                       
    query += f'&market={market}'
    query += f'&limit={limit}'


    response = requests.get(query,                                          
                   headers={"Content-Type":"application/json", 
                            "Authorization":f"Bearer {token}"})  
    json_response = response.json()                                           


    for i in range(len(json_response['shows']['items'])):                      

        id_list.append(json_response['shows']['items'][i]['id'])               
        name_list.append(json_response['shows']['items'][i]['name'])           
        desc_list.append(json_response['shows']['items'][i]['description'])
        
        
    more_runs = (json_response['shows']['total'] // 50 )                 
        
    counter += 1                                                    
    
    offset = offset + 50 
    
podcasts = pd.DataFrame()

podcasts['id'] = id_list
podcasts['name'] = name_list
podcasts['description'] = desc_list
print(podcasts)

#FULL LIST OF SHOWS TO SAVE FOR LATER
show_list = list(podcasts['id'])
 
    

show_id_list = []                                      
id_list = []
dur_list = []
date_list = []
name_list = []
desc_list = []

for show_id in show_list:                               
    
    more_runs = 1                                       
    counter = 0    
    
    id = show_id                                       
    type = 'episodes'
    market  = 'US'                                     
    limit = 50
    offset = 0                                

                                                             
    while((offset <= 1950) & (counter <= more_runs)):        
    
        endpoint_url = f"https://api.spotify.com/v1/shows/{id}/episodes?"

        query = f'{endpoint_url}'
        query += f'&q={search}'                              
        query += f'&type={type}'
        query += f'&offset={offset}'
        query += f'&market={market}'
        query += f'&limit={limit}'

        response = requests.get(query,                                      
                       headers={"Content-Type":"application/json", 
                                "Authorization":f"Bearer {token}"})
        json_response = response.json()                                     
        

        offset = offset + 50                                     
        counter += 1                                             
        

        if next(iter(json_response)) != 'error':                 
        
            for i in range(len(json_response['items'])):                       

                show_id_list.append(show_id)
                id_list.append(json_response['items'][i]['id'])                 
                dur_list.append(json_response['items'][i]['duration_ms'])       
                date_list.append(json_response['items'][i]['release_date'])    
                name_list.append(json_response['items'][i]['name'])
                desc_list.append(json_response['items'][i]['description'])
                
            more_runs = (json_response['total'] // 50 )              
        
        else:                                                                      
            offset = 1000000
            print(json_response, ' for show id: ', show_id)
            



all_episodes = pd.DataFrame()

all_episodes['show_id'] = show_id_list
all_episodes['episode_id'] = id_list
all_episodes['length(ms)'] = dur_list
all_episodes['date'] = date_list
all_episodes['episode_name'] = name_list
all_episodes['description'] = desc_list


# create a dictionary of show ids and show names
fmap = podcasts.groupby('id')['name'].apply(list).to_dict()

# map dictionary to show id in dataframe
all_episodes['show_id'] = all_episodes['show_id'].map(fmap)

# rename the show id column to show name
all_episodes.rename(columns = {'show_id':'show_name'}, inplace = True)

# remove the brackets [] from each show name
all_episodes['show_name'] = all_episodes['show_name'].str[0]


all_episodes.to_csv('datascience_podcasts.csv')