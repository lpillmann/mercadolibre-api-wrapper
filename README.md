# Mercado Libre's API Wrapper 

## Intro
Repository with code and notebooks used to work with Mercado Libre's API.

## How to use
For now, just create a Jupyter notebook in root folder and import module:
```
import mercadolibre as ml
```

See notebook `wrapper-example.ipynb`.

## What is implemented

- Basic wrapper for querying ML's API (`mercadolibre`)
	- Search by **keywords**, product **category**, **seller** id or all combined (`ml.get_df_from_query`)
	- Page visits for chosen items of given df (`ml.get_visits_df`)
	- Category info from a category ID (`ml.get_category_info`)
		- Get category name from a category ID (`ml.get_category_name`)
		- Get children categories from category ID (`ml.get_children_categories`)
	- Sellers by category with market share (`ml.get_sellers_by_category`)
	- Seller profile page from ID (`ml.seller_profile_url`)

- Extra handy tools
	- **Category explorer**: helps finding subcategory IDs (see notebook `categories-explorer.ipynb`)
	- Fix query and category names to be printed (e.g. in chart titles)

## TODOs

- <s>Category navigation</s> ("manual" navigation, `categories-explorer.ipynb`)
	- Go from parent to children and vice-versa
- Which category?
	- Get item's category to later further search
	- Obs.: it's already available as a column in df returned by `ml.get_df_from_query`
	- Maybe make a simple function to get for a single item?
- Play around with trends
	- What can we get from that?
- <s>Get all products from a seller</s>
	- Total revenue --> how big are they?
	- Avg. ticket price
- *Combine sellers' data with categories
	- Compare a seller's performance with products in category
	- Compare a seller's performance with other sellers in similar categories*
- <s>Rank sellers and analyse segmentation</s> (`ml.get_sellers_by_category`)
	- *Which ones should we target?*
