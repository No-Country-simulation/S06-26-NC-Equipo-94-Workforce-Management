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

np.random.seed(42)  # Reproducibilidad: mismos resultados al correr el script

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
print(f"Columnas descartadas: {col_eli}") # Advierte sobre las columnas eliminadas

# Conversión de fechas
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

print("Generando métricas operativas...") # Agrega nuevas columnas para análisis

# A. Logro de Objetivos (%) basado en columna 'Performance Score'
rangos_performance = {
    'Fully Meets':        (0.85, 0.99),
    'Exceeds':            (1.00, 1.25),
    'Needs Improvement':  (0.60, 0.84),
    'PIP':                (0.30, 0.59),
}

def generar_logro(categoria):
    """Genera un valor aleatorio dentro del rango correspondiente a la categoría.
    Si la categoría no está clasificada, usa un valor por defecto de 0.75."""
    rango = rangos_performance.get(categoria, None)
    if rango is None:
        return 0.75
    return np.random.uniform(rango[0], rango[1])

# Nueva columna de objetivos a partir de columna Performance Score
df_empleados['Logro_Objetivos_Emp'] = df_empleados['Performance Score'].apply(generar_logro)

# Verifica categorías no clasificadas
categorias_unicas = df_empleados['Performance Score'].dropna().unique()
no_mapeadas = [c for c in categorias_unicas if c not in rangos_performance]
if no_mapeadas:
    print(f"AVISO: Categorías de Performance Score sin rango definido (se usó 0.75): {no_mapeadas}")

# Flag de rotación (útil para validaciones rápidas)
df_empleados['Rotacion_Num'] = df_empleados['EmployeeStatus'].apply(
    lambda x: 1 if 'Terminated' in str(x) else 0
)

print("Logro_Objetivos_Emp generado correctamente.")

# ============================================================
# Tabla de calendario mensual (2018-08 a 2023-06)
# ============================================================

print("\nGenerando tabla de Calendario (nivel DÍA, continuo para Power BI)...")

fecha_inicio = pd.Timestamp('2018-08-01')

# fecha_fin se calcula dinámicamente a partir del máximo real entre StartDate y ExitDate,
# en lugar de un valor fijo, para que el Calendario siempre cubra el rango completo de los datos
# (evita dejar fuera empleados con fechas más recientes de lo esperado).
fecha_max_datos = max(df_empleados['StartDate'].max(), df_empleados['ExitDate'].max())
fecha_fin = (fecha_max_datos + pd.offsets.MonthEnd(0)).normalize()  # Fin del mes que contiene la fecha máxima

print(f"Fecha máxima detectada en los datos (StartDate/ExitDate): {fecha_max_datos.strftime('%Y-%m-%d')}")
print(f"Calendario se generará hasta: {fecha_fin.strftime('%Y-%m-%d')} (fin de ese mes)")

# Periodos mensuales (para construir Metricas_Regionales)
periodos = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='MS')  # MS = Month Start

# Calendario a nivel DÍA: Power BI necesita un "Date table" que no tenga huecos entre fechas consecutivas
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

# ===========================================================
# Generando métricas regionales mensuales (State x Periodo)
# ===========================================================

print("\nGenerando Métricas_Regionales mensuales...")

estados_unicos = df_empleados['State'].dropna().unique() # Identifica los estados unicos
print(f"Estados detectados: {len(estados_unicos)} -> {list(estados_unicos)}") # Los cuenta y menciona

# Valores base por estado (fijos por región, no cambian mes a mes)
base_regiones = {} # Diccionario vacio para almacenar resultados
for estado in estados_unicos: # Recorre la lista de estados unicos
    base_regiones[estado] = {
        'Costo_Fijo_Mensual_USD': np.random.randint(35000, 80000), # Asigna un costo fijo dentro del rango
        'Capacidad_Instalada_Horas': np.random.randint(1800, 3500), # Asigna una capacidad instalada dentro del rango
    }

# Construye fila por fila: State x Periodo
filas_regionales = [] # lista vacia para almacenar resultados

for estado in estados_unicos: # Recorre la lista de estados unicos
    # Desempaqueta los valores base por estado
    costo_base = base_regiones[estado]['Costo_Fijo_Mensual_USD']
    capacidad_instalada = base_regiones[estado]['Capacidad_Instalada_Horas']

    for periodo in periodos: # Recorre la lista de periodos
        # Aplica variación mensual de costo: +/- 5% sobre el costo base (simula ajustes menores)
        costo_mes = costo_base * np.random.uniform(0.95, 1.05)

        # Aplica variación mensual de utilización de capacidad: entre 60% y 96%
        pct_utilizacion = np.random.uniform(0.60, 0.96)
        capacidad_utilizada = capacidad_instalada * pct_utilizacion

        # Almacena resultados en lista vacia
        filas_regionales.append({ 
            'State': estado, 
            'Periodo': periodo,
            'Costo_Fijo_Mensual_USD': round(costo_mes, 2),
            'Capacidad_Instalada_Horas': capacidad_instalada,
            'Capacidad_Utilizada_Real_Horas': round(capacidad_utilizada, 0),
        })

df_regiones = pd.DataFrame(filas_regionales) # Convierte la lista de resultados en un Dataframe
# Genera nueva columna calculando la capacidad utilizada
df_regiones['Utilizacion_Capacidad'] = (
    df_regiones['Capacidad_Utilizada_Real_Horas'] / df_regiones['Capacidad_Instalada_Horas']
)

print(f"Metricas_Regionales generada: {len(df_regiones)} filas "
      f"({len(estados_unicos)} estados x {len(periodos)} meses).")


# ============================================================
# Genera logros a nivel regional (Logro_Objetivos_Regional)
# ============================================================

print("\nCalculando Logro_Objetivos_Regional (agregado desde empleados activos por mes)...")

# Un empleado se considera "activo" en un periodo (mes) si:
#   - Su StartDate es <= fin de ese mes
#   - Su ExitDate es NaT (sigue activo) o >= inicio de ese mes
# La lógica se aplica de forma vectorizada (máscara booleana) en lugar de fila por fila,
# para evitar loops anidados costosos sobre 3000 empleados x 61 meses.
logro_regional = [] # Lista vacia para almacenar resultados
for estado in estados_unicos: # Recorre la lista de estados unicos
    df_estado = df_empleados[df_empleados['State'] == estado] # Filtra los empleados por Estado

    for periodo in periodos: # Recorre la lista de periodos
        fin_mes = periodo + pd.offsets.MonthEnd(0)

        # Filtra a los empleados activos del mes
        mask_activos = (
            (df_estado['StartDate'] <= fin_mes) &
            (df_estado['ExitDate'].isna() | (df_estado['ExitDate'] >= periodo))
        )
        activos_mes = df_estado[mask_activos]

        if len(activos_mes) > 0:
            promedio_logro = activos_mes['Logro_Objetivos_Emp'].mean()
        else:
            # Si no hay empleados activos ese mes en ese estado, se utiliza un valor neutro
            promedio_logro = np.nan

        # Almacena resultados en lista vacia
        logro_regional.append({
            'State': estado,
            'Periodo': periodo,
            'Logro_Objetivos_Regional': promedio_logro,
        })

df_logro_regional = pd.DataFrame(logro_regional)

# Unimos con la tabla de métricas regionales a partir de State y Periodo
df_regiones = df_regiones.merge(df_logro_regional, on=['State', 'Periodo'], how='left')

# Si quedó algún NaN (meses sin empleados activos en ese estado), se queda vacío.
# Esto significa que: la empresa aún no tenía operaciones/empleados en ese estado en ese mes.

nulos_logro = df_regiones['Logro_Objetivos_Regional'].isna().sum()
if nulos_logro > 0:
    print(f"AVISO: {nulos_logro} filas State-Periodo sin empleados activos (quedan vacías, NO se rellenan). "
          f"Esto es esperado en los primeros meses si la empresa aún no operaba en ese estado.")

print("Logro_Objetivos_Regional calculado correctamente.")




# ==================================================
# Generación de archivo excel
# ==================================================

# Genera un nuevo archivo Excel con ambas pestañas: Base_Empleados, Métricas_Regionales y Calendario
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