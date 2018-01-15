import requests
import zipfile
import os

# DOI: 	10.6084/m9.figshare.5590852
# LINK https://doi.org/10.6084/m9.figshare.5590852.v1
db_url = 'https://ndownloader.figshare.com/files/9723037'
r = requests.get(db_url, allow_redirects=True)
fname = 'grid.zip'
open(fname, 'wb').write(r.content)
zip_ref = zipfile.ZipFile('grid.zip', 'r')
zip_ref.extractall('.')
zip_ref.close()
os.remove('grid.zip')
