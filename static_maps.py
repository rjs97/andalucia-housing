import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable


# SHAPEFILE
distrito_malaga = gpd.read_file(r'./shapefiles/malaga_distritos/da_cartografiaDistritoMunicipalPolygon.shp')
distrito_malaga = distrito_malaga.rename(columns={'NUMERO': 'DISTRITO'})

# VIVIENDAS TURISTICAS
viviendas_turisticas = pd.read_csv("./data/viviendas_turisticas_nov2024_dist.csv")

# filter + sort
viviendas_turisticas['DISTRITO'] = viviendas_turisticas['CUDIS'] % 100
viviendas_turisticas = viviendas_turisticas[['DISTRITO', 'vivienda turistica', 'plazas', 'plazas por vivienda turistica', 'Porcentaje vivienda turistica', 'PROV_LITERAL', 'MUN_LITERAL']]
viviendas_turisticas = viviendas_turisticas.rename(columns={'vivienda turistica': 'VIVIENDA TURISTICA', 'plazas': 'PLAZAS', 'plazas por vivienda turistica': 'PLAZAS POR VIVIENDA TURISTICA', 'Porcentaje vivienda turistica': '% VIVIENDA TURISTICA'})
viviendas_turisticas['% VIVIENDA TURISTICA'] = viviendas_turisticas['% VIVIENDA TURISTICA'].round(2)
viviendas_turisticas['PLAZAS POR VIVIENDA TURISTICA'] = viviendas_turisticas['PLAZAS POR VIVIENDA TURISTICA'].round(2)
malaga_vivienda = viviendas_turisticas[(viviendas_turisticas['PROV_LITERAL'] == 'Málaga') & (viviendas_turisticas['MUN_LITERAL'] == 'Málaga')].copy()

# merge and rename
distrito_malaga = distrito_malaga.merge(malaga_vivienda, on='DISTRITO')
distrito_malaga = distrito_malaga.rename(columns={'NOMBRE': 'NAME', 'DISTRITO': 'DISTRICT', 'VIVIENDA TURISTICA': 'TOURIST HOUSING UNITS', 'PLAZAS': 'RESIDENTIAL HOUSING UNITS', 'PLAZAS POR VIVIENDA TURISTICA': 'RESIDENTIAL PER TOURIST HOUSING UNIT', '% VIVIENDA TURISTICA': '% TOURIST HOUSING'})

# reshape map
distrito_malaga = distrito_malaga.to_crs(epsg=3857)

# reshape legend
_, ax = plt.subplots(1,1, figsize=(15,15))
divider = make_axes_locatable(ax)
cax = divider.append_axes("bottom", size="3%", pad=0.1)

for idx, row in distrito_malaga.iterrows():
    center = row['geometry'].centroid
    ax.text(center.x, center.y, s=row['NAME'], horizontalalignment='center', bbox={'facecolor': 'white', 'alpha':0.8, 'pad': 2, 'edgecolor':'none'})


vivienda_malaga = distrito_malaga.plot(
  column="% TOURIST HOUSING", 
  legend= True, 
  legend_kwds={"label": "Percentage of total apartments used for tourist rentals", "orientation": "horizontal"},
  alpha=0.7, 
  ax=ax,
  cax=cax,
  cmap="Greys",
  edgecolor="black"
)

vivienda_malaga.set_axis_off()

cx.add_basemap(vivienda_malaga, source=cx.providers.CartoDB.PositronNoLabels)

plt.savefig('./website/static/images/maps/vivienda_malaga.jpg')

# AIRBNB MALAGA
malaga_airbnb = pd.read_csv("./data/malaga_airbnb_20250328.csv")

# filter
malaga_airbnb = malaga_airbnb.dropna(subset=['price','availability_365'])
index_names = malaga_airbnb[(malaga_airbnb['price'] >= 5000) | (malaga_airbnb['price'] == 0) | (malaga_airbnb['availability_365'] == 0)].index
malaga_airbnb = malaga_airbnb.drop(index_names)

# calculations + normalizations
malaga_airbnb['PRICE/MONTH (€)'] = malaga_airbnb['price'].astype('float') * malaga_airbnb['availability_365'] / 12
malaga_airbnb['NAME'] = malaga_airbnb['neighbourhood'].str.upper()
malaga_airbnb['TOTAL AIRBNBS'] = malaga_airbnb[malaga_airbnb['room_type'] == 'Entire home/apt'].groupby('NAME')['id'].transform('size')

# group data by district
malaga_airbnb = malaga_airbnb[malaga_airbnb['room_type'] == 'Entire home/apt'][['PRICE/MONTH (€)','NAME', 'TOTAL AIRBNBS']].groupby(['NAME', 'TOTAL AIRBNBS'], as_index=False)['PRICE/MONTH (€)'].mean().round(2)

# create output
distrito_malaga = distrito_malaga.merge(malaga_airbnb, on='NAME')

airbnb_malaga = distrito_malaga.plot(
  column="PRICE/MONTH (€)", 
  legend= True, 
  legend_kwds={"label": "Monthly price of AirBnBs", "orientation": "horizontal"},
  alpha=0.7, 
  ax=ax,
  cax=cax,
  cmap="Greys",
  edgecolor="black"
)

airbnb_malaga.set_axis_off()

cx.add_basemap(airbnb_malaga, source=cx.providers.CartoDB.PositronNoLabels)

plt.savefig('./website/static/images/maps/airbnb_malaga.jpg')



