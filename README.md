# Projeto A 

## Intro
Repository with code and notebooks used to work with Mercado Libre's API.

## How to use
For now, just create a Jupyter notebook in root folder and import module:
```
import mercadolibre as ml
```

See notebook `wrapper-example.ipynb`.

## What is implemented

- Basic wrapper for querying ML's API
	- Search by keywords, product category or both combined
	- Get page visits for chosen items of given df
	- Get category name from a category ID
- Extra handy tools
	- Fix query and category names to be printed (e.g. in chart titles)

## TODOs

- Category navigation
	- Go from parent to children and vice-versa
- Which category?
	- Get item's category to later further search
	- Obs.: it's already available as a column in df returned by `get_df_from_query`
	- Maybe make a simple function to get for a single item?
- Play around with trends
	- What can we get from that?
- Get all products from a seller
	- Total revenue --> how big are they?
	- Avg. ticket price
- Combine sellers' data with categories
	- Compare a seller's performance with products in category
	- Compare a seller's performance with other sellers in similar categories
- Rank sellers and analyse segmentation
	- Which ones should we target?