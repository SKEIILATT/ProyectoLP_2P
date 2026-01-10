# RAG-EDU: Sistema de Análisis Educativo con IA

### Materia: Lenguajes de Programación – ESPOL

**Integrantes:**
- Javier Gutiérrez
- Jair Palaguachi

---

## Descripción

Sistema inteligente que combina visualización de datos y consultas con IA para analizar el abandono estudiantil universitario. Utiliza RAG (Retrieval-Augmented Generation) con Ollama, LangChain y ChromaDB.

### Características Principales

**Dashboard Interactivo**
- 3 KPIs principales (estudiantes, abandonos, tasa)
- 3 gráficas con Recharts (barras, pastel, líneas)
- Datos reales de Ecuador 2022 (159,333 estudiantes)

**Chatbot IA**
- Consultas en lenguaje natural
- Respuestas basadas en RAG
- Análisis de factores de riesgo
- Historial de conversación

**Datos Integrados**
- Ecuador 2022: SENESCYT (128,178 abandonos, 80.45% tasa)
- Dataset UCI: Portugal (4,424 estudiantes analizados)
- Jupyter notebooks con análisis estadístico

---

## Inicio Rápido

### Prerrequisitos

1. **Ollama** (IA Local)

```bash
# Descargar e instalar desde: https://ollama.ai
ollama serve
ollama pull mistral
```

2. **Python Dependencies**

```bash
cd backend-python
pip install -r requirements.txt
```

3. **Node Dependencies**

```bash
cd frontend
npm install
```

### Ejecutar el Sistema

```bash
# Terminal 1 - Laravel
cd backend-php
php artisan serve

# Terminal 2 - Python RAG
cd backend-python/rag
python rag_api.py

# Terminal 3 - React
cd frontend
npm run dev
```

Abrir: http://localhost:5173

---

## Arquitectura

```
React Frontend (localhost:5173)
    |
Laravel API (localhost:8000)
    |
Python RAG API (localhost:5000)
    |
ChromaDB + Ollama (Mistral)
```

---

## Módulos del Sistema

### 1. Módulo de Abandono Estudiantil

**Dashboard Visual:**
- Total estudiantes matriculados
- Total abandonos
- Tasa de deserción
- Abandono por tipo de institución
- Distribución por sexo
- Tendencia mensual

**Chat IA:**
- Consultas sobre datos Ecuador 2022
- Análisis dataset UCI (factores de riesgo)
- Preguntas de ejemplo integradas

**Fuentes de Datos:**
- Dataset UCI (analizado en Jupyter)
- SENESCYT Ecuador 2022 (scraping)

### 2. Módulo de Rendimiento Académico

Pendiente de implementación

---

## Tecnologías

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Recharts (visualizaciones)
- Tailwind CSS (estilos)
- Axios (HTTP client)

**Backend PHP:**
- Laravel 11
- API REST
- Proxy a Python RAG

**Backend Python:**
- Flask (API RAG)
- LangChain + LangChain-Ollama
- ChromaDB (vector database)
- Pandas + NumPy (análisis)
- BeautifulSoup (scraping)

**IA:**
- Ollama (inferencia local)
- Mistral (modelo LLM)
- nomic-embed-text (embeddings)

---

## Estructura del Proyecto

```
ProyectoLP_2P/
├── backend-php/                 # Laravel API
│   ├── app/Http/Controllers/Api/
│   │   ├── AbandonoController.php
│   │   └── RagController.php
│   └── routes/api.php
│
├── backend-python/              # Python RAG + Data Science
│   ├── data/
│   │   ├── raw/                # Dataset UCI
│   │   ├── processed/          # CSVs Ecuador
│   │   └── analysis/           # Jupyter notebooks
│   ├── rag/
│   │   ├── rag_api.py         # API REST Flask
│   │   ├── rag_query.py       # Sistema RAG
│   │   └── rag_ingest.py      # Carga documentos
│   └── scraping/              # Web scraping
│
├── frontend/                    # React App
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navigation.tsx
│   │   │   ├── AbandonoDashboard.tsx
│   │   │   └── ChatBot.tsx
│   │   └── App.tsx
│   └── package.json
│
└── README.md
```

---

## Datos y Hallazgos

### Ecuador 2022 (SENESCYT)

- Total Matriculados: 159,333 estudiantes
- Total Abandonos: 128,178 estudiantes
- Tasa Deserción: 80.45%

**Por Tipo de Institución:**
- Pública: 82.61% deserción
- Particular Cofinanciada: 75.27%
- Particular Autofinanciada: 77.55%

**Por Sexo:**
- Mujeres: 81.69% deserción
- Hombres: 78.76% deserción

### Dataset UCI (Análisis en Jupyter)

**Factores de Riesgo Identificados:**

1. **Becas:** Factor protector más fuerte
   - Sin beca: 29% abandono
   - Con beca: 3% abandono
   - Reducción: 9.6x menos probabilidad

2. **Rendimiento Académico 1er Semestre:**
   - Aprobar 2 materias o menos = alto riesgo
   - Predictor perfecto del 2do semestre

3. **Edad de Ingreso:**
   - Estudiantes mayores de 23 años: mayor riesgo
   - Perfil exitoso: 18-21 años

---

## Endpoints API

### Laravel (http://localhost:8000/api)

```bash
GET  /api/abandono/stats      # Estadísticas dashboard
POST /api/rag/query           # Consulta al chatbot
GET  /api/rag/health          # Estado del servicio
GET  /api/rag/models          # Modelos disponibles
```

### Python RAG (http://localhost:5000)

```bash
POST /api/rag/query           # Consulta directa
GET  /health                  # Health check
GET  /api/rag/models          # Lista modelos
```

---

## Ejemplos de Uso

### Dashboard

1. Navegar a http://localhost:5173
2. Click en "Dashboard"
3. Explorar visualizaciones

### Chat IA

1. Click en "Chat IA"
2. Escribir pregunta:
   - ¿Cuántos estudiantes abandonaron en 2022?
   - ¿Cómo afectan las becas al abandono?
   - ¿Qué factores predicen el riesgo de abandono?
3. Recibir respuesta basada en datos reales

---

## Metodología

Desarrollo Colaborativo Completo

Ambos integrantes participan en:
- Frontend (React/TypeScript)
- Backend (Laravel + Python)
- Data Science (Jupyter/Pandas)
- Integración de sistemas

---

## Licencia

Proyecto académico - ESPOL 2024/2025

---

## Estado del Proyecto

**Módulo Abandono Estudiantil (Completo)**
- Dashboard visual
- Chatbot RAG
- Datos Ecuador 2022
- Análisis UCI integrado

**Módulo Rendimiento Académico (Pendiente)**
- Dataset Open University
- Dashboard
- Chat IA
