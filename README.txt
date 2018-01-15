This is written by Chaitanya Chintaluri
GNU GPL v3.0 License.

Useful functions to fetch the city and country from the database of institutes.

Usage,

> python fetch_db.py

to obtain the https://www.grid.ac website which provides a db of institute names

> python affiliations_utils.py

Uses grid.ac db to disambiguate institute names - and gets back city and country names which are necessary fields https://www.grid.ac/format

Then use geopy to fetch the latitute and longitude of a city, country


