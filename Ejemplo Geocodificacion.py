import pandas as pd
import geopy
# import folium
from collections import defaultdict
import requests
import time
import geocoder
import json
# import os
import logging
# from geopy.distance import geodesic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

## Se prueba la geocodoficación con datos de direcciones de centros comerciales, que ya cuentan con
## información geocodificada y verificada

def _get_dataframe_centros_comerciales():
    """
    carga los datos csv de centros comerciales y crea el campo calle y n°
    :return: df y listas con información para geocodificar
    """
    df = pd.read_csv('centros_comerciales.csv', encoding='latin-1', sep=';')

    nombres = list(df['Nombre'])

    list_calle = []
    list_num = []
    for n in nombres:
        df_f = df[df['Nombre']==n]
        direccion = list(df_f['Direccion'])[0]
        calle,numero = direccion.split('-')[0].strip(),direccion.split('-')[1].strip()
        list_calle.append(calle)
        list_num.append(numero)

    df['Calle']=list_calle
    df['Número']=list_num

    return df

def _GEOCOD_OSM():
    """
    Geocodificación de centros comerciales usando Open Street Map con datos del dataframe
    :return: diccionario tipo json con direcciones geocodificadas
    """
    df = _get_dataframe_centros_comerciales()
    service = geopy.Nominatim(user_agent='Mozilla/5.0 (Windows NT 6.3; WOW64')

    lista_calles = list(df['Calle'])
    lista_ciudad = list(df['Comuna'])
    lista_numero = list(df['Número'])
    lista_region = list(df['Region'])
    lista_pais = list(df['Pais'])
    lista_dir_numero = list(df['Direccion'])

    geocodifica = 0
    no_geocodifica = 0
    lista_no_geocodifica = []
    dicc_direcciones_OSM = defaultdict(None)

    for i in range(len(lista_calles)):
        lat_long = None
        calle = lista_calles[i]
        ciudad = lista_ciudad[i]
        numero = lista_numero[i]
        region = lista_region[i]
        pais = lista_pais[i]
        dir_numero = lista_dir_numero[i]
        print(i)
        print(calle,numero,ciudad,region,pais)
        try:
            locationObj = service.geocode('{},{},{},{},{}'.format(calle,numero,ciudad,region,pais))

            print(locationObj)
            print(calle, ciudad)

            if locationObj is None:
                print(i, 'el valor de la geocodificaicón es None')
                if calle.__contains__('CALLE'):  ## para corroborar si el error es porque contiene la palabra calle
                    print('si tiene nombre calle')
                    calle = calle.replace('CALLE', '')
                    print(calle)
                    try:
                        locationObj = service.geocode('{},{},{},{},{}}'.format(calle,numero,ciudad,region,pais))
                        latitud = locationObj.latitude
                        longitud = locationObj.longitude
                        print(i, latitud, longitud)

                        lat_long = (latitud, longitud)
                        print(lat_long)
                        dicc_direcciones_OSM[dir_numero] = lat_long
                        print(dicc_direcciones_OSM)
                        geocodifica += 1
                    except Exception as e:
                        print(e)
                        print('no funciono eliminando el calle')

                elif calle.__contains__('Ñ'):
                    print('tiene una Ñ')
                    calle = calle.replace('Ñ', 'N')
                    print(calle)
                    try:
                        locationObj = service.geocode('{},{},{},{},{}'.format(calle,numero,ciudad,region,pais))
                        latitud = locationObj.latitude
                        longitud = locationObj.longitude
                        print(i, latitud, longitud)

                        lat_long = (latitud, longitud)
                        print(lat_long)
                        dicc_direcciones_OSM[dir_numero] = lat_long
                        print(dicc_direcciones_OSM)

                        geocodifica += 1
                    except Exception as e:
                        print(e)
                        print('no funciono eliminando la Ñ')
                else:
                    lista_no_geocodifica.append('{},{},Chile'.format(calle, ciudad))
                    no_geocodifica += 1
            else:
                latitud = locationObj.latitude
                longitud = locationObj.longitude
                print(i, latitud, longitud)

                lat_long = (latitud, longitud)
                print(lat_long)
                dicc_direcciones_OSM[dir_numero] = lat_long
                print(dicc_direcciones_OSM)

                geocodifica += 1
        except Exception as e:
            print(e)

        print('Proxima consulta en 3 segundo')
        time.sleep(3)

    print('¿Cuantos ha geocodificado?:', geocodifica)
    print('¿Cuantos no pudo geocodificar porque no encontró la calle?:', no_geocodifica)
    print('diccionario', dicc_direcciones_OSM)

    with open('dicc_direcciones.json', 'w', encoding="utf-8") as outfile:
        logger.info('Guardado el diccionario')
        # guarda json
        json.dump(dicc_direcciones_OSM, outfile)

    return dicc_direcciones_OSM
