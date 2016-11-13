import requests
import pandas as pd
from pandas import Series, DataFrame

import numpy as np
import datetime as dt
from tqdm import tqdm

def get_df_from_query(query, items_per_query, total_results_limit):
	
	#query = input('Qual a busca desejada? ')

	offset = 0
	received_itens = 0
	results = []

	payload = {'q': str(query), 'limit': str(1), 'offset': str(offset)}

	url = 'https://api.mercadolibre.com/sites/MLB/search'#?q=' + query +'&limit=' + str(items_per_query)
	print('Buscando por "' + query + '"')
	data = requests.get(url, params=payload).json()

	limit_itens = 0
	total_itens = data['paging']['total']	

	results = data['results'] # saves content from json in variable
	df = DataFrame(results) # converts to a pandas df

	# simple check for value sanity
	if (total_results_limit == None) or (total_results_limit > total_itens):
	    limit_itens = total_itens
	else:
	    limit_itens = total_results_limit
	    
	#print(str(limit_itens) + ' itens sendo transferidos. Aguarde...')
	#print(str(total_itens) + ' resultados encontrados no ML.')

	payload['limit']  = str(items_per_query) # sets limit

	pbar = tqdm(total=limit_itens) # initializes progress bar

	while len(df) < limit_itens:
	    # calculations or progress bar
	    old_length = len(df)
	    remaining = limit_itens - old_length
	    limit = items_per_query if remaining > items_per_query else remaining+1
	    
	    # updates query params
	    payload['offset'] = str(offset)
	    payload['limit']  = str(limit)
	    
	    data = requests.get(url, params=payload).json()
	    results = data['results'] # saves content from json in variable
	    df_new = DataFrame(results)
	    new_length = len(df_new)
	    
	    # concatenates new results to df
	    df.reset_index(drop=True)
	    df = pd.concat([df, df_new], axis=0) 
	    
	    # updates variables for next loop
	    offset = offset + new_length 
	    pbar.update(new_length)

	pbar.close()

	# selects a subset of columns, sorts by sold_quantity and fixes index

	df = df[['id', 'title', 'price', 'sold_quantity', 'available_quantity', 'permalink', 'thumbnail', 'seller_address', 'seller', 'stop_time']]
	df = df.sort_values('sold_quantity', ascending=False) # sorts df by most important column (to be defined, e.g. sold_quantity)
	#ids = df.id.values[0:ITEMS_TO_PLOT] # gets top sold items ML ids in a list
	df = df.set_index('id') # sets index to id

	# sorts items by sold quantity and deletes duplicates with less sales (assuming they'd be 0)
	df = df.sort_values(by='sold_quantity', ascending=False)
	df = df.drop_duplicates(subset=['title'], keep='first')

	# calculates total sold quantity
	total_sold_quantity = df['sold_quantity'].sum()

	# adds revenue column by an operation with sold_quantity and price
	df['revenue'] = df['sold_quantity'] * df['price']
	total_revenue = df['revenue'].sum()

	# fixes 'stop_time' to proper date format
	df['stop_time'] = pd.to_datetime(df['stop_time'])

	# calculates start time and days ago
	start_times = []
	days_ago = []

	today = dt.datetime.today()

	# iterates over df to calculate 'start_time' subtracting 20 years from the 'stop_time' (value of 20 is default for ML's data)
	for index, row in df.iterrows():
	    stop_time = df.loc[index, 'stop_time']
	    #df['start_time'][index] = date.replace(year = date.year - 20)
	    start = stop_time
	    start = start.replace(year = start.year - 20)
	    ago = (today - start).days

	    days_ago.append(ago)
	    start_times.append(start)
	    #print(str(start) + ' ' + str(stop_time))

	df['start_time'] = start_times
	df['days_ago'] = days_ago

	# extracting info from json/dict objects in cells
	cities = [] # empty list to hold city names
	states = [] # empty list to hold state names
	sellers =[] # empty list to hold sellers ids

	for index, row in df.iterrows():
	    cities.append(row['seller_address']['city']['name'])    
	    states.append(row['seller_address']['state']['name'])    
	    sellers.append(row['seller']['id'])    

	df['city'] = cities
	df['state'] = states
	df['seller_id'] = sellers

	df = df.sort_index()

	return df

