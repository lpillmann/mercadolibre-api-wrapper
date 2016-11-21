"""
Wrapper for Mercado Libre's API.

-------------
November 2016

"""

import requests
import pandas as pd
import datetime as dt
from tqdm import tqdm

def get_df_from_query(query='', category='', seller_id='',  items_per_query='200', total_results_limit=0):
    """
    Gets items using ML's public API search engine. 
    Uses multiple requests when there are more than 200 results.
    Performs basic data cleaning removing duplicates.

    Parameters
    ----------
    query : str
            search argument

    category : str
            ML category within which to search

    seller_id : str
            ML seller identification number

    items_per_query : str
            how many results per request (max = 200)

    total_results_limit : str
            maximum results to be downloaded, if 0 gets all available

    Returns
    -------
    df : Pandas DataFrame
        DataFrame of all results, without duplicates and following columns:
        ['title', 'price', 'sold_quantity', 'available_quantity', 'permalink',
       'thumbnail', 'seller_address', 'seller', 'stop_time', 'revenue'*,
       'start_time'*, 'days_ago'*, 'city'*, 'state'*, 'seller_id'*] 

       * calculated columns (not included in standard API response)
    """

    # Checks if arguments are valid and quits if not
    if (query == '' or query == None) and (category == '' or category == None) \
        and (seller_id == '' or seller_id == None):
        
        print('Please provide valid inputs to be searched.')
        return
    else:
        if (seller_id == '' or seller_id == None):
            payload = {'q': str(query), 'category': str(category), 'limit': str(1), 'offset': str(0)}
        # Only if seller_id is valid it is included in payload
        else:
            payload = {'q': str(query), 'category': str(category), 'seller_id': str(seller_id), 'limit': str(1), 'offset': str(0)}

    # Fixes names to later print eventually
    if query == '' or query == None:
        query_name = 'N/A'
    else:
        query_name = query

    if (category == '') or (category == None):
        category_name = 'N/A'
    else:
        # Gets category name
        url = 'https://api.mercadolibre.com/categories/' + category
        data = requests.get(url, params=payload).json()
        category_name = data['name']

    if seller_id == '' or seller_id == None:
        seller_name = 'N/A'
    else:
        seller_name = seller_id
    
    # Initial query to get how many results available
    #payload = {'q': str(query), 'limit': str(1), 'offset': str(0)}
    results = []
    url = 'https://api.mercadolibre.com/sites/MLB/search'
    print('Searching for "' + query_name + '" in '+ category_name + ' sold by ' + seller_name + '...')
    api_request = requests.get(url, params=payload)
    data = api_request.json()
    total_itens = data['paging']['total']  # How many results available


    if total_itens == 0:
        print('No results found. Please try other search parameters.')
        return

    print(str(total_itens) + ' results found.')

    results = data['results']
    df = pd.DataFrame(results) # Initiatializes main df to be used later in the while loop

    # Simple sanity check for the limit of itens to be requested
    if (total_results_limit == 0) or (total_results_limit > total_itens):
        limit_itens = total_itens
    else:
        limit_itens = total_results_limit
        
    # Prints general info about query
    #print(str(total_itens) + ' results found in ML.')
    #print(str(limit_itens) + ' items being transfered. Please wait...')

    pbar = tqdm(total=limit_itens)  # Initializes progress bar

    # Main loop to make multiple requests to get total results
    offset = 0

    while len(df) < limit_itens:
        # Calculations or progress bar
        old_length = len(df)
        remaining = limit_itens - old_length
        limit = items_per_query if remaining > items_per_query else remaining+1
        
        # Updates query params
        payload['offset'] = str(offset)
        payload['limit']  = str(limit)
        
        data = requests.get(url, params=payload).json()
        results = data['results']
        df_new = pd.DataFrame(results)
        new_length = len(df_new)
        
        # Concatenates new results to df
        df.reset_index(drop=True)
        df = pd.concat([df, df_new], axis=0) 
        
        # Updates variables for next loop
        offset = offset + new_length 
        pbar.update(new_length)

    pbar.close()

    print('Initial request sent to API: ' + api_request.url)

    # Selects a subset of columns and fixes index
    df = df[['id', 'title', 'price', 'sold_quantity', 'available_quantity', 'permalink' \
        , 'thumbnail', 'seller_address', 'seller', 'stop_time', 'category_id']]
    df = df.set_index('id') 

    # Sorts items by sold quantity and deletes duplicates with less sales (assuming they'd be 0)
    df = df.sort_values(by='sold_quantity', ascending=False)
    df = df.drop_duplicates(subset=['title'], keep='first')

    df['revenue'] = df['sold_quantity'] * df['price']  # Adds revenue column by an operation with sold_quantity and price
    df['stop_time'] = pd.to_datetime(df['stop_time'])  # Fixes 'stop_time' to proper date format

    # Calculates start time and days ago
    start_times = []
    days_ago = []
    today = dt.datetime.today()

    # Iterates over df to calculate 'start_time' subtracting 20 years from \
    # the 'stop_time' (value of 20 is default for ML's data)
    for index, row in df.iterrows():
        stop_time = df.loc[index, 'stop_time']
        start = stop_time
        start = start.replace(year = start.year - 20)
        ago = (today - start).days
        days_ago.append(ago)
        start_times.append(start)

    df['start_time'] = start_times
    df['days_ago'] = days_ago

    # Extracting info from json/dict objects in cells
    cities = [] 
    states = [] 
    sellers =[]

    for index, row in df.iterrows():
        cities.append(row['seller_address']['city']['name'])    
        states.append(row['seller_address']['state']['name'])    
        sellers.append(str(row['seller']['id']))    

    df['city'] = cities
    df['state'] = states
    df['seller_id'] = sellers

    df = df.sort_index()

    return df

def get_visits_df(main_df, num_items, sort_by='revenue', unit='day', time_ago=365):
    """
    Gets amount of page visits for certain ML items.

    Parameters
    ----------
    main_df : Pandas DataFrame
            df used as data source (format as returned by 'get_df_from_query')

    num_items : str
            how many itens whose visits will be requested (max = 50)

    sort_by : str
            sorts main_df by this parameter

    unit : str
            time unit with which to look back ('day' or 'hour')

    time_ago : str
            amount of days or hours, depending on 'unit'

    Returns
    -------
    visits_df : Pandas DataFrame
        DataFrame of all visits to requested items. Index in date format and \
        a column per item with # of visits.
        
    """
    if num_items > 50:
        num_items = 50
        print('Warning: maximum number of items is 50.')
        print('Resuming with num_items = 50...')

    # Makes comma-separated string from list to use in API multiget
    ids = main_df.sort_values(sort_by, ascending=False).index.values[0:num_items]
    ids_string = ','.join(ids)

    payload = {'ids': ids_string, 'last': time_ago, 'unit': unit}
    url = 'https://api.mercadolibre.com/items/visits/time_window'
    data = requests.get(url, params=payload).json()

    visits_df = pd.DataFrame(data[0]['results']) # initializes a df with the first item
    visits_df = visits_df[['date', 'total']] # gets only main columns
    visits_df.columns = ['date', data[0]['item_id']] # renames 'total' to item's ID

    # Iterates over data items to merge all 'total' columns into same df
    for item in data[1:]:
        results = item['results']
        s = pd.DataFrame(results).total
        s = s.rename(item['item_id'])
        visits_df = pd.concat([visits_df, s], axis=1)

    # Fixes df, parsing 'date' properly and setting as index column
    visits_df['date'] = pd.to_datetime(visits_df['date'])
    visits_df = visits_df.set_index('date')

    return visits_df

def get_categories(site='MLB'):
    """Returns main categories from ML site"""  
    url = 'https://api.mercadolibre.com/sites/' + site + '/categories'
    categories = requests.get(url).json()
    return categories


def get_category_info(category_id):
    """Returns info from provided ML category id""" 
    url = 'https://api.mercadolibre.com/categories/' + category_id
    category_info = requests.get(url).json()
    return category_info


def get_category_name(category_id):
    """Returns name from provided ML category id""" 
    url = 'https://api.mercadolibre.com/categories/' + category_id
    data = requests.get(url).json()
    category_name = data['name']
    return category_name


# *NOT WORKING*
# def get_all_children_categories(category):
#     """Recursive procedure to get all categories nested within one provided."""
#     children_categories = get_category_info(category)['children_categories']
#     if len(children_categories) == 0:
#         return children_categories
#     else:
#         for item in children_categories:
#             item['children_categories'] = get_children_categories(item['id'])
#             print(item['name'])
        
        
def get_children_categories(category):
    """Returns categories one level below the one provided."""
    return get_category_info(category)['children_categories']



"""
Handy tools for dealing with Mercado Libre's API data.
-------------
November 2016
"""

def fix_names_query_category(query, category):
    """Returns query and category names from ML code and 'N/A' if empty, e.g., to be printed in charts."""
    if (query == '' or query == None) and (category == '' or category == None):
        print('Please provide either a query or category.')
        return
    else:
        pass

    if query == '' or query == None:
        query_name = 'N/A'
    else:
        query_name = query

    if (category == '') or (category == None):
        category_name = 'N/A'
    else:
        # Gets category name
        category_name = get_category_name(category)

    return query_name, category_name
