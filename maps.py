import pandas as pd
import geopandas as gpd
import numpy as np

# SHAPEFILES
distrito_malaga = gpd.read_file(r'./shapefiles/malaga_distritos/da_cartografiaDistritoMunicipalPolygon.shp')
distrito_sevilla = gpd.read_file(r'./shapefiles/sevilla_distritos/Distritos_de_Sevilla.shp')

# RESHAPE
distrito_malaga = distrito_malaga.rename(columns={'NUMERO': 'DISTRITO'})

# https://sig.urbanismosevilla.org/TR_DistritosGU.aspx
sevilla_cod_distrito = { 'DISTRITO': np.arange(1,12), 'Distri_11D': ['Casco Antiguo', 'Macarena', 'Nervión', 'Cerro - Amate', 'Sur', 'Triana', 'Norte', 'San Pablo - Santa Justa', 'Este - Alcosa - Torreblanca', 'Bellavista - La Palmera', 'Los Remedios']}
distrito_sevilla = distrito_sevilla.merge(pd.DataFrame(data=sevilla_cod_distrito), on='Distri_11D')
distrito_sevilla['NOMBRE'] = distrito_sevilla['Distri_11D'].str.upper()
distrito_sevilla = distrito_sevilla[['NOMBRE', 'DISTRITO', 'geometry']]

# VIVIENDAS TURISTICAS
viviendas_turisticas = pd.read_csv("./data/viviendas_turisticas_nov2024_dist.csv")

# filter + sort
viviendas_turisticas['DISTRITO'] = viviendas_turisticas['CUDIS'] % 100
viviendas_turisticas = viviendas_turisticas[['DISTRITO', 'vivienda turistica', 'plazas', 'plazas por vivienda turistica', 'Porcentaje vivienda turistica', 'PROV_LITERAL', 'MUN_LITERAL']]
viviendas_turisticas = viviendas_turisticas.rename(columns={'vivienda turistica': 'VIVIENDA TURISTICA', 'plazas': 'PLAZAS', 'plazas por vivienda turistica': 'PLAZAS POR VIVIENDA TURISTICA', 'Porcentaje vivienda turistica': '% VIVIENDA TURISTICA'})
viviendas_turisticas['% VIVIENDA TURISTICA'] = viviendas_turisticas['% VIVIENDA TURISTICA'].round(2)
viviendas_turisticas['PLAZAS POR VIVIENDA TURISTICA'] = viviendas_turisticas['PLAZAS POR VIVIENDA TURISTICA'].round(2)
malaga_vivienda = viviendas_turisticas[(viviendas_turisticas['PROV_LITERAL'] == 'Málaga') & (viviendas_turisticas['MUN_LITERAL'] == 'Málaga')].copy()
sevilla_vivienda = viviendas_turisticas[(viviendas_turisticas['PROV_LITERAL'] == 'Sevilla') & (viviendas_turisticas['MUN_LITERAL'] == 'Sevilla')].copy()

# merge
distrito_malaga = distrito_malaga.merge(malaga_vivienda, on='DISTRITO')
distrito_sevilla = distrito_sevilla.merge(sevilla_vivienda, on='DISTRITO')


# create outputs
vivienda_malaga = distrito_malaga.explore(column='% VIVIENDA TURISTICA', tiles='CartoDB positron', tooltip=['NOMBRE', 'DISTRITO', 'VIVIENDA TURISTICA', 'PLAZAS', 'PLAZAS POR VIVIENDA TURISTICA', '% VIVIENDA TURISTICA'])
vivienda_sevilla = distrito_sevilla.explore(column='% VIVIENDA TURISTICA', tiles='CartoDB positron', tooltip=['NOMBRE', 'DISTRITO', 'VIVIENDA TURISTICA', 'PLAZAS', 'PLAZAS POR VIVIENDA TURISTICA', '% VIVIENDA TURISTICA'])
vivienda_malaga.save('./website/templates/vivienda_malaga_es.html')
vivienda_sevilla.save('./website/templates/vivienda_sevilla_es.html')

distrito_malaga_en = distrito_malaga.rename(columns={'NOMBRE': 'NAME', 'DISTRITO': 'DISTRICT', 'VIVIENDA TURISTICA': 'TOURIST HOUSING UNITS', 'PLAZAS': 'RESIDENTIAL HOUSING UNITS', 'PLAZAS POR VIVIENDA TURISTICA': 'RESIDENTIAL PER TOURIST HOUSING UNIT', '% VIVIENDA TURISTICA': '% TOURIST HOUSING'})
distrito_sevilla_en = distrito_sevilla.rename(columns={'NOMBRE': 'NAME', 'DISTRITO': 'DISTRICT', 'VIVIENDA TURISTICA': 'TOURIST HOUSING UNITS', 'PLAZAS': 'RESIDENTIAL HOUSING UNITS', 'PLAZAS POR VIVIENDA TURISTICA': 'RESIDENTIAL PER TOURIST HOUSING UNIT', '% VIVIENDA TURISTICA': '% TOURIST HOUSING'})

vivienda_malaga = distrito_malaga_en.explore(column='% TOURIST HOUSING', tiles='CartoDB positron', tooltip=['NAME', 'DISTRICT', 'TOURIST HOUSING UNITS', 'RESIDENTIAL HOUSING UNITS', 'RESIDENTIAL PER TOURIST HOUSING UNIT', '% TOURIST HOUSING'])
vivienda_sevilla = distrito_sevilla_en.explore(column='% TOURIST HOUSING', tiles='CartoDB positron', tooltip=['NAME', 'DISTRICT', 'TOURIST HOUSING UNITS', 'RESIDENTIAL HOUSING UNITS', 'RESIDENTIAL PER TOURIST HOUSING UNIT', '% TOURIST HOUSING'])


vivienda_malaga.save('./website/templates/vivienda_malaga_en.html')
vivienda_sevilla.save('./website/templates/vivienda_sevilla_en.html')

# AIRBNB MALAGA
malaga_airbnb = pd.read_csv("./data/malaga_airbnb_20250328.csv")

# filter
malaga_airbnb = malaga_airbnb.dropna(subset=['price','availability_365'])
index_names = malaga_airbnb[(malaga_airbnb['price'] >= 5000) | (malaga_airbnb['price'] == 0) | (malaga_airbnb['availability_365'] == 0)].index
malaga_airbnb = malaga_airbnb.drop(index_names)

# calculations + normalizations
malaga_airbnb['PRECIO/MES (€)'] = malaga_airbnb['price'].astype('float') * malaga_airbnb['availability_365'] / 12
malaga_airbnb['NOMBRE'] = malaga_airbnb['neighbourhood'].str.upper()
malaga_airbnb['AIRBNB TOTAL'] = malaga_airbnb[malaga_airbnb['room_type'] == 'Entire home/apt'].groupby('NOMBRE')['id'].transform('size')

# group data by district
malaga_airbnb = malaga_airbnb[malaga_airbnb['room_type'] == 'Entire home/apt'][['PRECIO/MES (€)','NOMBRE', 'AIRBNB TOTAL']].groupby(['NOMBRE', 'AIRBNB TOTAL'], as_index=False)['PRECIO/MES (€)'].mean().round(2)

# create output
distrito_malaga = distrito_malaga.merge(malaga_airbnb, on='NOMBRE')
malaga_output = distrito_malaga.explore(column='PRECIO/MES (€)', tiles='CartoDB positron', tooltip=['NOMBRE', 'DISTRITO', 'PRECIO/MES (€)', 'AIRBNB TOTAL'])
malaga_output.save('./website/templates/airbnb_malaga_es.html')

distrito_malaga_en = distrito_malaga.rename(columns={'NOMBRE': 'NAME', 'DISTRITO': 'DISTRICT', 'PRECIO/MES (€)': 'PRICE/MONTH (€)', 'AIRBNB TOTAL': 'TOTAL AIRBNBS'})
malaga_output = distrito_malaga_en.explore(column='PRICE/MONTH (€)', tiles='CartoDB positron', tooltip=['NAME', 'DISTRICT', 'PRICE/MONTH (€)', 'TOTAL AIRBNBS'])
malaga_output.save('./website/templates/airbnb_malaga_en.html')


# AIRBNB SEVILLA
sevilla_airbnb = pd.read_csv("./data/sevilla_airbnb_20250326.csv")

# filter
sevilla_airbnb = sevilla_airbnb.dropna(subset=['price','availability_365'])
index_names = sevilla_airbnb[(sevilla_airbnb['price'] >= 5000) | (sevilla_airbnb['price'] == 0) | (sevilla_airbnb['availability_365'] == 0)].index
sevilla_airbnb = sevilla_airbnb.drop(index_names)

# calculations + normalizations
sevilla_airbnb['PRECIO/MES (€)'] = sevilla_airbnb['price'].astype('float') * sevilla_airbnb['availability_365'] / 12
sevilla_airbnb['NOMBRE'] = sevilla_airbnb['neighbourhood_group'].str.upper()
# normalize "Norte" and "Bellavista - Palmera"
sevilla_airbnb['NOMBRE'] = sevilla_airbnb['NOMBRE'].str.replace('MACARENA - NORTE', 'NORTE').str.replace('PALMERA - BELLAVISTA', 'BELLAVISTA - LA PALMERA')
sevilla_airbnb['AIRBNB TOTAL'] = sevilla_airbnb[sevilla_airbnb['room_type'] == 'Entire home/apt'].groupby('NOMBRE')['id'].transform('size')

# group data by district
sevilla_airbnb = sevilla_airbnb[sevilla_airbnb['room_type'] == 'Entire home/apt'][['PRECIO/MES (€)','NOMBRE', 'AIRBNB TOTAL']].groupby(['NOMBRE', 'AIRBNB TOTAL'], as_index=False)['PRECIO/MES (€)'].mean().round(2)

# create output
distrito_sevilla = distrito_sevilla.merge(sevilla_airbnb, on='NOMBRE')
sevilla_output = distrito_sevilla.explore(column='PRECIO/MES (€)', tiles='CartoDB positron', tooltip=['NOMBRE', 'DISTRITO', 'PRECIO/MES (€)', 'AIRBNB TOTAL'])
sevilla_output.save('./website/templates/airbnb_sevilla_es.html')

distrito_sevilla_en = distrito_sevilla.rename(columns={'NOMBRE': 'NAME', 'DISTRITO': 'DISTRICT', 'PRECIO/MES (€)': 'PRICE/MONTH (€)', 'AIRBNB TOTAL': 'TOTAL AIRBNBS'})
sevilla_output = distrito_sevilla_en.explore(column='PRICE/MONTH (€)', tiles='CartoDB positron', tooltip=['NAME', 'DISTRICT', 'PRICE/MONTH (€)', 'TOTAL AIRBNBS'])
sevilla_output.save('./website/templates/airbnb_sevilla_en.html')
