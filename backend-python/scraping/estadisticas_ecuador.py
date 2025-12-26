'''
Script de Web Scraping - Estadísticas Educativas Ecuador Descarga y procesa datos de deserción estudiantil desde la página de SENESCYT
'''
import requests #Libreria que utilizaré para hacer peticiones HTTP
import pandas as pd
import os #Libreria para interactuar con el so (sistema operativo)
from datetime import datetime 

# Deshabilitar warnings de SSL (el servidor de SENESCYT tiene certificado no verificable)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

'''
Para realizar el scraping, se está utilizando este sitio web que recopila información estadística en Ecuador sobre el tema de deserción 
https://siau.senescyt.gob.ec/estadisticas-de-educacion-superior-ciencia-tecnologia-e-innovacion/
'''

#URLs de descarga del repositorio que el SENESCYT brinda
URL_NUMERADOR = "https://cloud-pro.senescyt.gob.ec/public.php/dav/files/FjESnmBkDksaYRp/Numeradordeserción2022_300924.xlsx"
URL_DENOMINADOR = "https://cloud-pro.senescyt.gob.ec/public.php/dav/files/FjESnmBkDksaYRp/Denominadordeserción2022_300924.xlsx"

#Rutas donde guardar los archivos
CARPETA_DATOS = "../datos/estadisticas_ecuador"
ARCHIVO_NUMERADOR = os.path.join(CARPETA_DATOS, "numerador_desercion_2022.xlsx")
ARCHIVO_DENOMINADOR = os.path.join(CARPETA_DATOS, "denominador_desercion_2022.xlsx")

def descargar_archivo(url, ruta_destino):
    'Esta función me permite descargar un archivo desde una url (haciendo scraping) y lo guarda de manera local en la carpeta de datos'
    print(f"Descargando: {url}")
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        with open(ruta_destino, "wb") as archivo:
            archivo.write(response.content)
        print(f"Descargado de manera exitosa: {ruta_destino}")
        return True
    else:
        print(f"Error al descargar. Error de tipo : {response.status_code}")
        return False

def main():
    'Función principal que hace todo el proceso de scraping'
    
    #Creo la carpeta si no existe
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    #Descargo los archivos
    print("Descargando archivos desde repositorio SENESCYT")
    descargar_archivo(URL_NUMERADOR,ARCHIVO_NUMERADOR)
    descargar_archivo(URL_DENOMINADOR, ARCHIVO_DENOMINADOR)
    print("Scraping completado exitosamente")
    print(f"Se guardaron los archivos en {CARPETA_DATOS}")

if __name__=="__main__":
    main()