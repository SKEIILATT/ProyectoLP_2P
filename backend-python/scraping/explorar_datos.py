import pandas as pd

# Cargar el archivo del numerador

excel_file = pd.ExcelFile("../datos/estadisticas_ecuador/numerador_desercion_2022.xlsx")

# Ver qué hojas tiene el archivo
print(f"\nHojas disponibles: {excel_file.sheet_names}")
print()

# Ver las primeras filas de cada hoja
for hoja in excel_file.sheet_names:
    print(f"\n--- Hoja: {hoja} ---")
    df = pd.read_excel(excel_file, sheet_name=hoja, nrows=10)
    print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"Columnas: {list(df.columns)}")
    print(df.head())
    print()

# Ahora explorar el denominador
print("EXPLORANDO: Denominador de Deserción 2022")

excel_file2 = pd.ExcelFile("../datos/estadisticas_ecuador/denominador_desercion_2022.xlsx")

# Ver qué hojas tiene el archivo
print(f"\nHojas disponibles: {excel_file2.sheet_names}")
print()

# Ver las primeras filas de cada hoja
for hoja in excel_file2.sheet_names:
    print(f"\n--- Hoja: {hoja} ---")
    df = pd.read_excel(excel_file2, sheet_name=hoja, nrows=10)
    print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"Columnas: {list(df.columns)}")
    print(df.head())
    print()

# Contar totales para ver si es que nuestra hipótesis de que el archivo numerador tiene unicamente la cantidad de estudiantes que abandonaron y que denominador tiene toda la cantidad de estudiantes, hayan abandonado o no. 

print("VERIFICACIÓN DE HIPÓTESIS")


numerador_completo = pd.read_excel("../datos/estadisticas_ecuador/numerador_desercion_2022.xlsx")
denominador_completo = pd.read_excel("../datos/estadisticas_ecuador/denominador_desercion_2022.xlsx")

print(f"\nTotal filas NUMERADOR: {len(numerador_completo):,}")
print(f"Total filas DENOMINADOR: {len(denominador_completo):,}")

if len(denominador_completo) > len(numerador_completo):
    print("\nDenominador > Numerador")
    print("  Esto confirma que:")
    print("  - Numerador = estudiantes que ABANDONARON")
    print("  - Denominador = TODOS los estudiantes matriculados")
else:
    print("\nHIPÓTESIS INCORRECTA - Necesitamos investigar más")
