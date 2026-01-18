"""
Script de Web Scraping - Estadísticas Educativas Ecuador
Descarga y procesa datos de deserción estudiantil desde SENESCYT
"""
import requests
import pandas as pd
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL_NUMERADOR = "https://cloud-pro.senescyt.gob.ec/public.php/dav/files/FjESnmBkDksaYRp/Numeradordeserción2022_300924.xlsx"
URL_DENOMINADOR = "https://cloud-pro.senescyt.gob.ec/public.php/dav/files/FjESnmBkDksaYRp/Denominadordeserción2022_300924.xlsx"

CARPETA_DATOS = "../data/processed/estadisticas_ecuador"
ARCHIVO_NUMERADOR = os.path.join(CARPETA_DATOS, "numerador_desercion_2022.xlsx")
ARCHIVO_DENOMINADOR = os.path.join(CARPETA_DATOS, "denominador_desercion_2022.xlsx")

def descargar_archivo(url, ruta_destino):
    """Descarga un archivo desde una URL y lo guarda localmente"""
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        with open(ruta_destino, "wb") as archivo:
            archivo.write(response.content)
        return True
    return False

def procesar_datos():
    """Procesa los excel descargados del scraping"""
    numerador = pd.read_excel(ARCHIVO_NUMERADOR)
    denominador = pd.read_excel(ARCHIVO_DENOMINADOR)
    tasa_desercion = (len(numerador) / len(denominador) * 100)
    return numerador, denominador, tasa_desercion

def generar_estadisticas(numerador, denominador):
    """Genera estadísticas detalladas y las guarda en CSV"""
    desercion_sexo = numerador["sexo"].value_counts()
    total_sexo = denominador["sexo"].value_counts()
    stats_sexo = pd.DataFrame({
        'Estudiantes_Abandonaron': desercion_sexo,
        'Total matriculados': total_sexo,
        'Tasa Desercion': (desercion_sexo / total_sexo * 100).round(2)
    })
    archivo_stats_sexo = os.path.join(CARPETA_DATOS, "desercion_por_sexo.csv")
    stats_sexo.to_csv(archivo_stats_sexo)

    desercion_tipo = numerador['tipo_financiamiento'].value_counts()
    total_tipo = denominador['tipo_financiamiento'].value_counts()

    stats_tipo = pd.DataFrame({
        'Estudiantes_Abandonaron': desercion_tipo,
        'Total_Matriculados': total_tipo,
        'Tasa_Desercion_%': (desercion_tipo / total_tipo * 100).round(2)
    })

    archivo_tipo = os.path.join(CARPETA_DATOS, "desercion_por_tipo_institucion.csv")
    stats_tipo.to_csv(archivo_tipo)
    return stats_sexo, stats_tipo

def generar_resumen_general(numerador, denominador, tasa_general):
    """Genera un CSV con el resumen general de deserción"""
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
    return resumen

def main():
    """Función principal del proceso de scraping"""
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    descargar_archivo(URL_NUMERADOR, ARCHIVO_NUMERADOR)
    descargar_archivo(URL_DENOMINADOR, ARCHIVO_DENOMINADOR)

    numerador, denominador, tasa = procesar_datos()
    generar_estadisticas(numerador, denominador)
    generar_resumen_general(numerador, denominador, tasa)

    print("Scraping y procesamiento completado.")

if __name__ == "__main__":
    main()
