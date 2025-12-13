# CONCLUSIONES FINALES - ANÁLISIS DE ABANDONO ESTUDIANTIL

Este análisis exploró los factores asociados al abandono estudiantil utilizando el dataset de abandono de UCI con **4,424 estudiantes**. Se identificaron factores académicos, socioeconómicos y demográficos con diferentes niveles de impacto.

**Tasa General de Abandono: 32.12%** - Casi 1 de cada 3 estudiantes abandona sus estudios.

---

## TOP 5 FACTORES MÁS CRÍTICOS

### RENDIMIENTO ACADÉMICO DEL 1ER SEMESTRE (Factor Determinante)

**Hallazgos Cuantitativos:**
- **Dropout**: mediana de 2 materias aprobadas, nota promedio 7.26
- **Graduate**: mediana de 6 materias aprobadas, nota promedio 12.64
- **Diferencia crítica**: 4 materias y 5.4 puntos de calificación

**Impacto:**
- Correlación 1er→2do semestre: **r=0.90** (predicción casi perfecta)
- Aprobar ≤2 materias en 1er semestre = **riesgo extremo** de colapso en 2do semestre
- IQR Dropout=4.0 vs Graduate=2.0 (alta variabilidad vs perfil estable)

**Conclusión:**
> El 1er semestre es el predictor más fuerte de abandono. La ventana crítica de intervención es **durante y después del 1er semestre**.

---

### 2️⃣ BECAS (Factor Protector Más Fuerte - 26pp de reducción)

**Hallazgos Cuantitativos:**
- Sin beca: **29.09%** de abandono
- Con beca: **3.03%** de abandono
- **Reducción: 26.06 puntos porcentuales**

**Impacto:**
- Los estudiantes sin beca tienen **9.6x más probabilidad** de abandonar
- Solo 24.8% de estudiantes tienen beca (1,099 de 4,424)
- Las becas son el factor protector institucional más efectivo

**Conclusión:**
> Expandir el programa de becas es la política de retención más efectiva. Las becas no solo previenen el abandono, sino que crean condiciones para el éxito académico.

---

### COLAPSO EN 2DO SEMESTRE (Momento de No Retorno)

**Hallazgos Cuantitativos:**
- **Dropout**: rendimiento cae de mediana 2.0 → **0.0** materias aprobadas
- **Graduate**: mantiene consistencia 6.0 → 6.0 materias
- **>50% de quienes abandonan** aprueban 0 materias en 2do semestre

**Impacto:**
- El abandono se **materializa** en el 2do semestre (no es deterioro gradual, es colapso)
- La transición 1er→2do semestre marca el punto de no retorno

**Conclusión:**
> Las intervenciones post-1er semestre son **URGENTES**. Los estudiantes que aprueban ≤2 materias deben recibir apoyo inmediato entre semestres.

---

### EDAD AL INGRESO (Estudiante No Tradicional en Riesgo)

**Hallazgos Cuantitativos:**
- **Dropout**: mediana 23 años, promedio 26 años
- **Graduate**: mediana 19 años, promedio 22 años
- **Diferencia**: 4 años promedio

**Impacto:**
- Estudiantes >23 años tienen mayor riesgo de abandono
- IQR Graduate=3 años (perfil homogéneo) vs Dropout=11 años (heterogéneo)
- Rango extremo: estudiantes hasta 70 años en grupo Dropout

**Conclusión:**
> Estudiantes no tradicionales (>23 años) necesitan apoyos diferenciados: horarios flexibles, modalidades semipresenciales, programas acelerados.

---

### COMPROMISO FINANCIERO/DEUDAS (Indicador Contraintuitivo)

**Hallazgos Cuantitativos:**
- Sin deudas: **25.07%** de abandono
- Con deudas: **7.05%** de abandono
- Solo **11.37%** de estudiantes tiene deudas

**Impacto:**
- Tener deudas indica **permanencia/compromiso**, no riesgo
- Los que abandonan lo hacen ANTES de acumular deudas significativas
- Deudas requieren tiempo en el sistema (sesgo de selección)

**Conclusión:**
> Las deudas NO son factor de riesgo. El grupo de mayor riesgo: **sin beca Y sin deudas** (abandono temprano antes de invertir).

---

## JERARQUÍA DE FACTORES POR NIVEL DE IMPACTO

### NIVEL CRÍTICO (Predictores Directos):
- **Rendimiento 1er semestre**: Correlación r=0.90 con 2do semestre
- **Umbral de Alerta**: ≤2 materias aprobadas

### NIVEL ALTO (Factores Protectores >20pp):
- **Becas**: -26pp de abandono (factor protector más fuerte)

### NIVEL MODERADO (Factores de Contexto 10-20pp):
- **Edad**: Estudiantes >23 años en riesgo moderado (+4 años promedio)
- **Deudas**: -18pp (indicador de compromiso, no factor causal)

### NIVEL BAJO (<10pp):
- **Factores macroeconómicos**: Correlaciones débiles con abandono individual

---

## RECOMENDACIONES INSTITUCIONALES (Accionables)

### SISTEMA DE ALERTA TEMPRANA

**Implementar detección automática después del 1er semestre:**

✅ **Riesgo EXTREMO** (intervención inmediata):
- Aprobó ≤2 materias en 1er semestre
- Sin beca
- Edad >25 años

✅ **Riesgo ALTO**:
- Aprobó 3-4 materias
- Sin beca O edad >23 años

✅ **Riesgo MODERADO**:
- Aprobó 3-4 materias
- Con beca
- Edad tradicional (18-22)

---

### POLÍTICAS DE APOYO FINANCIERO

1. **Expansión de Becas**:
   - Priorizar estudiantes con rendimiento moderado (3-5 materias 1er sem)
   - Los becarios con bajo rendimiento necesitan también apoyo académico

2. **Becas de Emergencia**:
   - Otorgar becas de rescate a estudiantes en riesgo después del 1er semestre
   - Combinar con tutoría obligatoria

---

### INTERVENCIONES ACADÉMICAS

1. **Tutorías Intensivas**:
   - Entre 1er y 2do semestre para estudiantes en riesgo
   - Enfoque en materias críticas del 1er semestre

2. **Programa de Nivelación**:
   - Cursos de refuerzo antes del inicio del 1er semestre
   - Especialmente para estudiantes mayores retomando estudios

3. **Seguimiento Personalizado**:
   - Asignar mentores a estudiantes de alto riesgo
   - Reuniones semanales durante el 1er semestre

---

### APOYOS PARA ESTUDIANTES NO TRADICIONALES

1. **Flexibilidad Horaria**:
   - Secciones nocturnas/fines de semana
   - Modalidades semipresenciales/híbridas

2. **Servicios Complementarios**:
   - Guarderías en campus (estudiantes con hijos)
   - Reconocimiento de experiencia laboral (créditos)

3. **Programas Acelerados**:
   - Rutas más cortas para estudiantes con experiencia previa


