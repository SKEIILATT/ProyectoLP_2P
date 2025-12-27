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
    
def procesar_datos():
    'Esta función me procesa los excel descargados anteriormente en el scraping'
    #Carga de datos
    print("Cargador numerador (estudiantes que abandonaron)")
    numerador = pd.read_excel(ARCHIVO_NUMERADOR)
    print("Cargador denominador (estudiantes matriculados)")
    denominador = pd.read_excel(ARCHIVO_DENOMINADOR)
    print(f"  - Total estudiantes que abandonaron: {len(numerador):,}")
    print(f"  - Total estudiantes matriculados: {len(denominador):,}")
    #Calculo de tasa de deserción
    tasa_desercion = (len(numerador)/len(denominador)*100)
    print(f"Tasa de deserción generada en 2022: {tasa_desercion}")
    return numerador, denominador, tasa_desercion 

def generar_estadisticas(numerador, denominador):
    "Función que genera estadísticas detalladas y las guarda en csv"
    #Estadística por Sexo
    desercion_sexo = numerador["sexo"].value_counts()
    total_sexo = denominador["sexo"].value_counts()
    stats_sexo = pd.DataFrame({
        'Estudiantes_Abandonaron':desercion_sexo,
        'Total matriculados': total_sexo,
        'Tasa Desercion': (desercion_sexo/total_sexo *100).round(2)
    })
    archivo_stats_sexo = os.path.join(CARPETA_DATOS, "desercion_por_sexo.csv")
    stats_sexo.to_csv(archivo_stats_sexo)
    print(f"Guardado correctamente {stats_sexo}")

    # 2. Estadísticas por TIPO DE FINANCIAMIENTO
    desercion_tipo = numerador['tipo_financiamiento'].value_counts()
    total_tipo = denominador['tipo_financiamiento'].value_counts()
    
    stats_tipo = pd.DataFrame({
        'Estudiantes_Abandonaron': desercion_tipo,
        'Total_Matriculados': total_tipo,
        'Tasa_Desercion_%': (desercion_tipo / total_tipo * 100).round(2)
    })
    
    archivo_tipo = os.path.join(CARPETA_DATOS, "desercion_por_tipo_institucion.csv")
    stats_tipo.to_csv(archivo_tipo)
    print(f"Guardado: desercion_por_tipo_institucion.csv")
    return stats_sexo, stats_tipo

def generar_resumen_general(numerador, denominador, tasa_general):
    """
    Genera un CSV con el resumen general de deserción
    """
    print("Generando resumen general")
    resumen = pd.DataFrame({
        'Indicador': [
            'Total Estudiantes Matriculados 2022',
            'Total Estudiantes que Abandonaron',
            'Total Estudiantes que Continuaron',
            'Tasa de Deserción (%)',
            'Tasa de Retención (%)'
        ],
        'Valor': [
            len(denominador),
            len(numerador),
            len(denominador) - len(numerador),
            round(tasa_general, 2),
            round(100 - tasa_general, 2)
        ]
    })
    
    archivo_resumen = os.path.join(CARPETA_DATOS, "resumen_general_desercion_2022.csv")
    resumen.to_csv(archivo_resumen, index=False)
    print(f"Guardado: resumen_general_desercion_2022.csv")
    
    return resumen



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

    #Procesar datos
    numerador, denominador, tasa = procesar_datos()
    #Genero estadisticas detalladas
    stats_sexo, stats_tipo = generar_estadisticas(numerador, denominador)
        
    # Generar resumen general
    resumen = generar_resumen_general(numerador, denominador, tasa)

    print()
    print("Scraping y procesamiento completo")
    print(f"Archivos guardados en {CARPETA_DATOS}")

if __name__=="__main__":
    main()