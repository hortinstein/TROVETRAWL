import pandas as pd
import numpy as np

# Create a base date
base_date = pd.to_datetime('2024-01-01')

# Generate date range
dates = pd.date_range(base_date, periods=50, freq='D')

# Sample ship names, with repetition
ship_names = np.random.choice(['Sea Explorer', 'Ocean Voyager', 'Marine Pioneer', 'Aqua Adventurer', 'Wave Rider'], size=50)

# Generate random latitudes and longitudes
latitudes = np.random.uniform(low=-90.0, high=90.0, size=50)
longitudes = np.random.uniform(low=-180.0, high=180.0, size=50)

# Schedule descriptions
sked_descriptions = np.random.choice([
    '01JAN24-05JAN24, UNDERWAY',
    '06JAN24-10JAN24, In transit',
    '11JAN24-15JAN24, PORT',
    '16JAN24-20JAN24, UNDERWAY',
    '21JAN24-25JAN24, In transit',
    '26JAN24-30JAN24, PORT'
], size=50)

# Create the DataFrame
data = {
    'date': dates,
    'sked': sked_descriptions,
    'shipname': ship_names,
    'lat': latitudes,
    'lon': longitudes
}

df = pd.DataFrame(data)
df.head(50)

df.to_csv('test.csv', index=False)