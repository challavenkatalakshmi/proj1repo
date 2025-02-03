import geopandas as gpd
import psycopg2
import json
from shapely.geometry import shape

import matplotlib.pyplot as plt
import folium

# Database connection parameters
DB_URI = "postgresql://postgres:1234@localhost/postgres"

# Create a psycopg2 connection
conn = psycopg2.connect(DB_URI)

# SQL query using ST_AsGeoJSON to get geometry as GeoJSON
query = "SELECT id, name, area, ST_AsGeoJSON(geom) as geom FROM parks"

# Execute the query
cur = conn.cursor()
cur.execute(query)

# Fetch all rows
rows = cur.fetchall()

# Create lists for the dataframe
data = []
for row in rows:
    # Convert the GeoJSON string to a Shapely geometry object
    geom = json.loads(row[3])  # The 4th column is the GeoJSON geometry
    geometry = shape(geom)

    data.append({
        'id': row[0],
        'name': row[1],
        'area': row[2],
        'geom': geometry
    })

# Create a GeoDataFrame
df = gpd.GeoDataFrame(data)

# Set the 'geom' column as the active geometry column
df.set_geometry('geom', inplace=True)

# Assign CRS (set to EPSG:4326 - WGS 84)
df.set_crs("EPSG:4326", allow_override=True, inplace=True)

# Close the connection
conn.close()

# Print the dataframe
print(df)
df.plot(figsize=(8, 6), color="green", markersize=df["area"] * 50)
plt.title("Urban Parks Distribution")
plt.show()

m = folium.Map(location=[40.75, -73.98], zoom_start=12)

# Add points to the map
for idx, row in df.iterrows():
    folium.Marker(
        location=[row['geom'].y, row['geom'].x],  # Correct way to access the geometry
        popup=f"{row['name']} ({row['area']} sq.km)",
        icon=folium.Icon(color="green")
    ).add_to(m)


# Save map
m.save("parks_map.html")


