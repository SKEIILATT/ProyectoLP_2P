'''
Script de WEB Scraping 
Extrae lista de universidades desde la página del ces para darle más contexto al RAG

'''
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Deshabilitar warnings de SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# URL base
URL_BASE = "https://www.ces.gob.ec/"
#URL DE UNIVERSIDADES PÚBLICAS
URL_PUBLICAS = "https://www.ces.gob.ec/?page_id=328"
# Carpeta de salida
CARPETA_DATOS = "../data/processed/estadisticas_ecuador"


def scrapear_universidades_publicas():
    """
    Scrapea la lista de universidades públicas del CES
    """
    print("WEB SCRAPING HTML: Universidades Ecuador - CES")
    print()
    
    # Hacer petición HTTP
    response = requests.get(URL_PUBLICAS, verify=False)
    
    if response.status_code != 200:
        print(f"Error: No se pudo acceder a la página (código {response.status_code})")
        return None
    
    print("Página descargada exitosamente")
    
    # Parsear HTML con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar la tabla
    tabla = soup.find('table', {'id': 'dataTables-publicas'})
    
    if not tabla:
        print("No se encontró la tabla")
        return None
    
    print("Tabla encontrada")
    
    return soup, tabla

def extraer_datos_tabla(tabla):
    """
    Extrae los datos de cada fila de la tabla
    """    
    universidades = []
    
    # Encontrar todas las filas del tbody
    filas = tabla.find('tbody').find_all('tr')
    
    for fila in filas:
        celdas = fila.find_all('td')
        
        if len(celdas) >= 5:
            codigo = celdas[0].get_text(strip=True)
            nombre = celdas[2].get_text(strip=True)
            provincia = celdas[3].get_text(strip=True)
            canton = celdas[4].get_text(strip=True)
            
            universidad = {
                'Codigo': codigo,
                'Nombre': nombre,
                'Provincia': provincia,
                'Canton': canton,
                'Tipo': 'Pública Nacional'
            }
            
            universidades.append(universidad)
    
    print(f"Extraídas {len(universidades)} universidades")
    
    return universidades

def guardar_csv(universidades):
    """
    Guarda los datos en CSV
    """
    print("\nPaso 4: Guardando datos en CSV...")
    
    # Crear carpeta si no existe
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    
    # Convertir a DataFrame
    df = pd.DataFrame(universidades)
    
    # Guardar CSV
    archivo_csv = os.path.join(CARPETA_DATOS, "universidades_publicas_ecuador.csv")
    df.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
    
    print(f"Guardado: {archivo_csv}")
    print(f"Total universidades: {len(df)}")
    
    return df


def main():
    """
    Función principal
    """
    # Scrapear página
    resultado = scrapear_universidades_publicas()
    
    if resultado is None:
        print("Error en el scraping")
        return
    
    soup, tabla = resultado
    
    # Extraer datos
    universidades = extraer_datos_tabla(tabla)
    
    # Guardar CSV
    df = guardar_csv(universidades)
    
    print("Scraping HTML completado exitosamente")



if __name__ == "__main__":
    main()

