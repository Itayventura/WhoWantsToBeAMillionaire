# import SRC.db_populator
# import requests
from db_populator import DatabasePopulator

mockValues = ["val1", "val2", "val3"]
dbp = DatabasePopulator()
dbp.sample_population(mockValues)

# TODO: use the request library to populate our database
