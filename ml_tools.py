"""
Handy tools for dealing with Mercado Libre's API data.

-------------
November 2016

"""

import ml_wrapper as ml

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
	    category_name = ml.get_category_name(category)

	return query_name, category_name