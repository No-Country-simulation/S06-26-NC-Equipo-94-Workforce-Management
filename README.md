# S06-26-NC-Equipo-94-Workforce-Management

# GlobalForce Workforce Analytics — Dashboard de RRHH Automatizado
 
El proyecto consiste en un pipeline end-to-end que genera un reporte ejecutivo mensual de Recursos Humanos con KPIs clave, distribuido automáticamente por correo a un stakeholder.
 
---
 
## 1. Resumen Ejecutivo
 
GlobalForce es una empresa especializada en gestión de fuerza laboral para organizaciones con operaciones distribuidas en múltiples regiones. El reporting ejecutivo periódico de desempeño operativo y financiero de sus equipos se realizaba de forma manual, consolidando datos de distintas fuentes en hojas de cálculo — un proceso lento y propenso a errores (hasta 3 días de trabajo por cliente).
 
Este proyecto propone y construye un prototipo de solución de **Business Intelligence** que automatiza la recolección, transformación, visualización y distribución de indicadores de workforce management.
 
## 2. Objetivo
 
Diseñar y construir una plataforma de BI que automatice la generación de reportes ejecutivos de workforce management, mediante:
 
- Reducción del tiempo de generación de reportes.
- Estandarización de métricas y criterios de cálculo.
- Incremento en la calidad y trazabilidad de los datos.
- Distribución automática del reporte final a stakeholders.
 
## 3. Arquitectura del Pipeline
 
```
Dataset (Kaggle / sintético)
        │
        ▼
Limpieza y preparación de datos (Python + Pandas)
        │
        ▼
Feature engineering (goal achievement, indicadores derivados)
        │
        ▼
Modelo de datos en Power BI (relaciones entre tablas)
        │
        ▼
Medidas DAX (KPIs)
        │
        ▼
Dashboard interactivo (Power BI)
        │
        ▼
Automatización con Power Automate
        │
        ▼
Exportación a PDF → Envío mensual por correo al stakeholder
```
 
## 4. Fuente y Preparación de Datos
 
- **Origen del dataset:** dataset de RRHH obtenido de Kaggle, combinado/complementado con datos sintéticos para cubrir las características necesarias para el análisis (headcount, costos, asignaciones, objetivos de desempeño).
- **Limpieza (`datos_limpieza.py`):** script en Python (Pandas) responsable de:
  - Estandarizar formatos y tipos de datos.
  - Corregir inconsistencias y valores faltantes.
  - Generar las columnas/features necesarias para calcular *goal achievement* y otros indicadores derivados.
- **Salida:** archivos CSV limpios, listos para ser consumidos por Power BI / Power Query.
 
## 5. Modelo de Datos y KPIs (Power BI + DAX)
 
El modelo dimensional en Power BI relaciona las tablas de empleados, asignaciones, costos y objetivos. Sobre este modelo se construyeron medidas DAX para los siguientes KPIs:
 
| Categoría | KPI |
|---|---|
| Capital Humano | Headcount activo, nuevas contrataciones, bajas, **turnover rate** |
| Productividad | Capacity utilization, horas facturables / no facturables, productividad por empleado |
| Finanzas | **Total cost**, costo por estado |
| Desempeño | **Goal achievement**, desviación de metas, indicadores de eficiencia |
 
 
## 6. Automatización (Power Automate)
 
Flujo configurado en Power Automate para:
 
1. Disparar el proceso mensualmente (programado).
2. Exportar el reporte/dashboard de Power BI a PDF.
3. Enviar el PDF por correo electrónico al stakeholder definido.
 
## 7. Tecnologías Utilizadas
 
| Componente | Tecnología |
|---|---|
| Generación y preparación de datos | Python + Pandas |
| Repositorio de archivos | Google Drive |
| Transformación de datos | Power Query |
| Modelado y visualización | Power BI (DAX) |
| Automatización y distribución | Power Automate |
| Exportación de reportes | PDF |
 
## 8. Alcance del Prototipo
 
**Incluido:**
- Generación/combinación de datos (Kaggle + sintéticos).
- Limpieza y feature engineering en Python.
- Modelo analítico y dashboard interactivo en Power BI.
- Automatización de exportación a PDF y envío por correo (Power Automate).
 
**Fuera de alcance (para esta versión):**
- Integración con sistemas productivos/ERP reales.
- Actualización de datos en tiempo real.
 
## 9. Limitaciones
 
- Uso de datos simulados/sintéticos con fines demostrativos.
- Actualización semiautomática del proceso (no en tiempo real).
- Dependencia de cargas periódicas de información.
 
## 10. Evolución Futura
 
- Integración con ERP y sistemas de RRHH reales.
- Automatización completa del pipeline (ingesta → dashboard → distribución).
- Modelos predictivos de rotación de personal.
- Análisis de capacidad y demanda mediante Machine Learning.
 
## 11. Enlaces del Proyecto
  
- **Repositorio de código (GitHub):** `<https://github.com/No-Country-simulation/S06-26-NC-Equipo-94-Workforce-Management.git>`
- **Dashboard publicado (Power BI Service):** `<https://app.fabric.microsoft.com/view?r=eyJrIjoiMjRmNzZjMDEtNTFkNC00NjA3LTg5OWItYmI1ZDEzYjhmZjE4IiwidCI6IjFmODEwNTkyLTJiMTAtNGQyZi05ZDFkLWNhMzFiMjY5MTVkZSIsImMiOjR9>`
- **Dataset / carpeta de datos (Google Drive):** `<enlace pendiente>`
- **Documento de framework / propuesta conceptual:** `<https://docs.google.com/document/d/1jU8Wb_MsmMeE9AmWmWBDQJAY8Shdxgzt-cUCSGR-dOY/edit?tab=t.0#heading=h.dti9y3lmio3y>`
 
## 12. Equipo
 
- `<S06-26-NC-Equipo-94-Workforce-Management>`

### Vista general

<img src="https://github.com/user-attachments/assets/b78a8092-61af-4dab-86ac-ada18ce2603e" width="900"/> 

<br><br>

### Análisis detallado

<img src="https://github.com/user-attachments/assets/54efbdd8-2abe-493b-b444-401d53939c66" width="900"/>
