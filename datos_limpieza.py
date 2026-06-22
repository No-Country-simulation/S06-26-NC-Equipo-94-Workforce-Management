"""
Script de generación de dataset para Dashboard GlobalForce
===========================================================
Genera tablas:
1. Base_empleados
2. Metricas_Regionales
3. Calendario

"""
import pandas as pd
import numpy as np

np.random.seed(42)  # Reproducibilidad: mismos resultados cada vez que corras el script

# =========================================================
# Carga de archivo employee_data.csv
# =========================================================

print("Cargando employee_data.csv...")
df_empleados = pd.read_csv('employee_data.csv')  # Carga del dataset 

# Columnas a eliminar | justificación :
# - ADEmail: datos sensible, irrelvante para análisis
# - Supervisor, BusinessUnit, RaceDesc: no es parte del alcance del análisis
# - TerminationDescription: texto sin formato específico, dificil de analizar y fuera del alcance
col_eli = ['ADEmail','Supervisor','BusinessUnit','TerminationDescription','RaceDesc'] 
df_empleados.drop(columns=col_eli, errors='ignore', inplace=True)
print(f"Columnas descartadas: {col_eli}") # Para advertir al usuario sobre las columnas eliminadas

# Conversión de fechas: el formato real es 'DD-Mon-YY' 
df_empleados['StartDate'] = pd.to_datetime(df_empleados['StartDate'], format='%d-%b-%y', errors='coerce')
df_empleados['ExitDate'] = pd.to_datetime(df_empleados['ExitDate'], format='%d-%b-%y', errors='coerce')

fechas_invalidas = df_empleados['StartDate'].isna().sum()
if fechas_invalidas > 0:
    print(f"AVISO: {fechas_invalidas} filas con StartDate no interpretable.")

print(f"Rango de StartDate: {df_empleados['StartDate'].min()} a {df_empleados['StartDate'].max()}")
print(f"Rango de ExitDate: {df_empleados['ExitDate'].min()} a {df_empleados['ExitDate'].max()}")


# ===========================================================
# Generando métricas operativas a nivel empleado (Logro_Objetivos)
# ===========================================================

print("Generando métricas operativas...") # Agregar nuevas columnas para análisis

# A. Logro de Objetivos (%) basado exactamente en tu columna 'Performance Score'
condiciones = [
    (df_empleados['Performance Score'] == 'Fully Meets'),
    (df_empleados['Performance Score'] == 'Excellent'),
    (df_empleados['Performance Score'] == 'Needs Improvement'),
    (df_empleados['Performance Score'] == 'PIP')
]

# Asignamos rangos de porcentaje para cada estado de desempeño, con un valor por defecto del 75% para cualquier estado no clasificado
valores = [
    np.random.uniform(0.85, 0.99, size=len(df_empleados)),  # Fully Meets: 85% a 99%
    np.random.uniform(1.00, 1.25, size=len(df_empleados)),  # Excellent: 100% a 125%
    np.random.uniform(0.60, 0.84, size=len(df_empleados)),  # Needs Improvement: 60% a 84%
    np.random.uniform(0.30, 0.59, size=len(df_empleados))   # PIP: 30% a 59%
]
# Si hay algún estado sin clasificar, por defecto le pone 75%
df_empleados['Logro_Objetivos'] = np.select(condiciones, valores, default=0.75)

# La columna original tiene los estados: 'Active', 'Voluntarily Terminated', 'Terminated', etc.
df_empleados['Rotacion_Num'] = df_empleados['EmployeeStatus'].apply(
    lambda x: 1 if 'Terminated' in str(x) else 0
)

print("Creando matriz de Métricas Regionales basadas en tus 'State'...") # Crear métrica regional simulada basada en los estados únicos de tu dataset
# Tomamos los estados únicos de tu columna 'State' (MA, ND, FL, etc.)
estados_unicos = df_empleados['State'].dropna().unique()

# Para cada estado, asignamos un costo fijo mensual y una capacidad instalada de horas, con valores aleatorios dentro de rangos razonables para simular la realidad
data_regiones = {
    'State': estados_unicos,
    'Costo_Fijo_Mensual_USD': [np.random.randint(35000, 80000) for _ in estados_unicos],
    'Capacidad_Instalada_Horas': [np.random.randint(1800, 3500) for _ in estados_unicos]
}

df_regiones = pd.DataFrame(data_regiones)

# Calculamos horas reales utilizadas y el porcentaje operativo final
df_regiones['Capacidad_Utilizada_Real_Horas'] = df_regiones['Capacidad_Instalada_Horas'].apply(
    lambda x: int(x * (np.random.randint(60, 96) / 100))
)
df_regiones['Utilizacion_Capacidad'] = df_regiones['Capacidad_Utilizada_Real_Horas'] / df_regiones['Capacidad_Instalada_Horas']


# ============================================================
# Tabla de calendario mensual (2018-08 a 2023-06)
# ============================================================

print("\nGenerando tabla de Calendario (nivel DÍA, sin huecos, requerido por Power BI)...")

fecha_inicio = pd.Timestamp('2018-08-01')
fecha_fin = pd.Timestamp('2023-06-30')  # Fin de mes, no solo el día 1

# Periodos mensuales (para construir Metricas_Regionales y Turnover_Referencia mensuales)
periodos = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='MS')  # MS = Month Start

# Calendario a nivel DÍA: Power BI exige que una "Date table" no tenga huecos entre fechas consecutivas
dias = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')

df_calendario = pd.DataFrame({'Fecha': dias})
df_calendario['Anio'] = df_calendario['Fecha'].dt.year
df_calendario['Mes'] = df_calendario['Fecha'].dt.month
df_calendario['NombreMes'] = df_calendario['Fecha'].dt.strftime('%B')
df_calendario['AnioMes'] = df_calendario['Fecha'].dt.strftime('%Y-%m')
# Columna clave para relacionar con Metricas_Regionales (que sigue siendo a nivel mes/Periodo):
# el primer día del mes de cada fecha. Esto permite la relación Calendario[PrimerDiaMes] -> Metricas_Regionales[Periodo]
df_calendario['PrimerDiaMes'] = df_calendario['Fecha'].values.astype('datetime64[M]')

print(f"Calendario generado: {len(df_calendario)} días "
      f"({dias.min().strftime('%Y-%m-%d')} a {dias.max().strftime('%Y-%m-%d')}), sin huecos.")


# ==================================================
# Generación de archivo excel
# ==================================================

# Generamos un nuevo archivo Excel con ambas pestañas: Base_Empleados, Métricas_Regionales y Calendario
archivo_final = 'Simulacion_Laboral_Dataset.xlsx'  
print(f"Guardando pestañas en {archivo_final}...")

with pd.ExcelWriter(archivo_final, engine='openpyxl') as writer:
    df_empleados.to_excel(writer, sheet_name='Base_Empleados', index=False)
    df_regiones.to_excel(writer, sheet_name='Metricas_Regionales', index=False)
    df_calendario.to_excel(writer, sheet_name='Calendario', index=False)

print("¡Todo listo! El proceso terminó sin errores.")
print(f"\nResumen de pestañas generadas en {archivo_final}:")
print(f"  - Base_Empleados:        {df_empleados.shape[0]} filas, {df_empleados.shape[1]} columnas")
print(f"  - Metricas_Regionales:   {df_regiones.shape[0]} filas, {df_regiones.shape[1]} columnas")
print(f"  - Calendario:            {df_calendario.shape[0]} filas")