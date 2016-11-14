# Projeto A 

## What is done

- Basic wrapper for querying ML's API
	- Search by keywords, product category or both combined
	- Get page visits data for chosen items
	- Get category name from ML's category ID
- Extra handy tools
	- Fix query and category names to be printed (e.g. in chart titles)

## Important TODOs

- Category navigation
	- Go from parent to children and vice-versa
- Which category?
	- Get item's category to later further search
	- Obs.: it's already available as a column in df returned by `get_df_from_query`
	- Maybe make a simple function to get for a single item?
- Play around with trends
	- What can we get from that?