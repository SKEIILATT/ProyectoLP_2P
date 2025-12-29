"""
Scraper para Recursos Educativos Abiertos
"""
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecursosEducativosScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
    
    def scrape_unesco_stats(self) -> str:
        """
        Extrae estadísticas de educación superior de UNESCO
        
        Returns:
            Texto con estadísticas
        """
        urls = [
            "http://uis.unesco.org/en/topic/higher-education"
        ]
        
        content = "# ESTADÍSTICAS UNESCO - EDUCACIÓN SUPERIOR\n\n"
        
        for url in urls:
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraer contenido principal
                main_content = soup.find('main') or soup.find('article')
                if main_content:
                    paragraphs = main_content.find_all(['p', 'li'])
                    for p in paragraphs[:20]:  # Limitar a 20 párrafos
                        text = p.get_text(strip=True)
                        if len(text) > 40:
                            content += f"{text}\n\n"
                
                logger.info(f"✓ Extraído contenido de UNESCO")
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"Error al extraer UNESCO {url}: {e}")
        
        return content
    
    def scrape_study_techniques(self) -> str:
        """
        Genera contenido sobre técnicas de estudio y retención estudiantil
        
        Returns:
            Texto con recursos educativos
        """
        content = """
# GUÍA DE TÉCNICAS DE ESTUDIO Y RETENCIÓN ESTUDIANTIL

## 1. TÉCNICAS DE ESTUDIO EFECTIVAS

### Método Pomodoro
Técnica de gestión del tiempo que consiste en dividir el trabajo en intervalos de 25 minutos,
separados por breves descansos. Mejora la concentración y reduce la fatiga mental.

### Mapas Mentales
Representación gráfica de ideas y conceptos que ayuda a organizar información de manera visual.
Facilita la comprensión de relaciones entre conceptos y mejora la memoria.

### Método Cornell
Sistema de toma de notas que divide la página en secciones: notas, palabras clave y resumen.
Promueve la revisión activa y la síntesis de información.

### Técnica Feynman
Consiste en explicar conceptos complejos con palabras simples, como si se enseñara a otra persona.
Identifica vacíos en el conocimiento y refuerza el aprendizaje.

### Repaso Espaciado
Técnica que distribuye el estudio a lo largo del tiempo en lugar de concentrarlo.
Aumenta la retención a largo plazo mediante revisiones periódicas.


## 2. FACTORES DE RETENCIÓN ESTUDIANTIL

### Integración Académica
- Participación activa en clases
- Relación con profesores
- Rendimiento académico satisfactorio
- Acceso a tutorías y apoyo académico

### Integración Social
- Construcción de redes de apoyo entre pares
- Participación en actividades extracurriculares
- Sentido de pertenencia institucional
- Adaptación al ambiente universitario

### Apoyo Institucional
- Servicios de orientación vocacional
- Asesoramiento psicológico
- Programas de nivelación
- Becas y ayudas económicas


## 3. ESTRATEGIAS DE PREVENCIÓN DEL ABANDONO

### Detección Temprana
- Sistemas de alerta temprana basados en asistencia y calificaciones
- Identificación de estudiantes en riesgo
- Intervención oportuna mediante tutorías

### Apoyo Personalizado
- Mentoría entre pares
- Asesoramiento académico individualizado
- Planes de estudio personalizados
- Seguimiento continuo del progreso

### Recursos Financieros
- Programas de becas por mérito y necesidad
- Opciones de financiamiento flexible
- Apoyo para materiales de estudio
- Oportunidades de trabajo-estudio


## 4. HABILIDADES DE AUTORREGULACIÓN

### Gestión del Tiempo
- Establecimiento de metas realistas
- Priorización de tareas
- Planificación semanal y mensual
- Balance entre estudios y vida personal

### Motivación y Persistencia
- Establecimiento de objetivos claros
- Celebración de logros pequeños
- Manejo de la frustración académica
- Desarrollo de resiliencia

### Metacognición
- Reflexión sobre el propio proceso de aprendizaje
- Identificación de fortalezas y debilidades
- Ajuste de estrategias según resultados
- Autoevaluación constante


## 5. RECURSOS DE APOYO DIGITAL

### Plataformas de Aprendizaje
- Khan Academy: Cursos gratuitos en múltiples áreas
- Coursera: Educación universitaria online
- edX: Cursos de universidades prestigiosas
- MIT OpenCourseWare: Recursos educativos abiertos

### Herramientas de Productividad
- Notion: Organización de notas y proyectos
- Trello: Gestión de tareas
- Forest: Aplicación para mantener concentración
- Anki: Sistema de repaso espaciado con flashcards


## 6. INDICADORES DE RIESGO DE ABANDONO

### Señales Académicas
- Descenso en el rendimiento académico
- Faltas recurrentes a clases
- No entrega de trabajos
- Dificultad para comprender contenidos

### Señales Personales
- Falta de motivación
- Dificultades económicas
- Problemas de salud mental
- Conflictos familiares

### Señales Institucionales
- Insatisfacción con la carrera elegida
- Falta de orientación vocacional
- Desconexión con la institución
- Ausencia de redes de apoyo


## 7. MEJORES PRÁCTICAS INSTITUCIONALES

### Programas de Inducción
- Orientación integral para nuevos estudiantes
- Familiarización con servicios institucionales
- Integración social temprana
- Clarificación de expectativas académicas

### Sistemas de Monitoreo
- Seguimiento continuo del desempeño
- Análisis predictivo de riesgo
- Alertas automatizadas para intervención
- Evaluación de efectividad de programas

### Cultura de Apoyo
- Ambiente institucional acogedor
- Promoción de la diversidad e inclusión
- Canales de comunicación abiertos
- Valoración del bienestar estudiantil

"""
        
        logger.info("✓ Generado contenido sobre técnicas de estudio")
        return content
    
    def scrape_open_resources(self) -> str:
        """
        Extrae información de recursos educativos abiertos
        
        Returns:
            Texto consolidado
        """
        logger.info("\n📚 Extrayendo recursos educativos abiertos...")
        
        all_content = "# RECURSOS EDUCATIVOS ABIERTOS Y ORIENTACIÓN ESTUDIANTIL\n\n"
        all_content += "=" * 80 + "\n\n"
        
        # UNESCO
        logger.info("🌍 Extrayendo estadísticas UNESCO...")
        unesco_content = self.scrape_unesco_stats()
        all_content += unesco_content + "\n" + "=" * 80 + "\n\n"
        
        # Técnicas de estudio
        logger.info("📖 Generando guía de técnicas de estudio...")
        study_content = self.scrape_study_techniques()
        all_content += study_content + "\n" + "=" * 80 + "\n\n"
        
        # Agregar referencias adicionales
        all_content += self._add_references()
        
        logger.info("✅ Extracción de recursos completada")
        return all_content
    
    def _add_references(self) -> str:
        """Agrega referencias bibliográficas"""
        return """
# REFERENCIAS Y RECURSOS ADICIONALES

## Bibliografía Recomendada

1. Tinto, V. (1993). Leaving College: Rethinking the Causes and Cures of Student Attrition.
   - Modelo teórico fundamental sobre abandono universitario

2. Astin, A. (1984). Student Involvement: A Developmental Theory for Higher Education.
   - Teoría sobre participación estudiantil y éxito académico

3. Bean, J. & Metzner, B. (1985). A Conceptual Model of Nontraditional Undergraduate Student Attrition.
   - Modelo conceptual de deserción en estudiantes no tradicionales

4. Braxton, J. (2000). Reworking the Student Departure Puzzle.
   - Análisis contemporáneo del problema de deserción

## Organizaciones y Recursos Online

- **IESALC UNESCO**: Instituto Internacional para la Educación Superior en América Latina y el Caribe
  URL: https://www.iesalc.unesco.org/

- **SENESCYT**: Secretaría de Educación Superior, Ciencia, Tecnología e Innovación (Ecuador)
  URL: https://www.educacionsuperior.gob.ec/

- **What Works Clearinghouse**: Base de evidencia científica sobre prácticas educativas
  URL: https://ies.ed.gov/ncee/wwc/

- **NSSE**: National Survey of Student Engagement
  URL: https://nsse.indiana.edu/

## Herramientas y Plataformas

- Khan Academy: https://www.khanacademy.org/
- Coursera: https://www.coursera.org/
- edX: https://www.edx.org/
- MIT OpenCourseWare: https://ocw.mit.edu/

"""
    
    def save_to_file(self, content: str, filepath: str):
        """Guarda el contenido en un archivo"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"💾 Guardado en: {filepath}")


# Script de ejecución
if __name__ == "__main__":
    scraper = RecursosEducativosScraper()
    
    # Extraer todos los recursos
    recursos_content = scraper.scrape_open_resources()
    
    # Guardar resultado
    import os
    os.makedirs('datos/papers_academicos', exist_ok=True)
    scraper.save_to_file(recursos_content, 'datos/papers_academicos/recursos_orientacion.txt')
    
    print("\n🎉 Scraping de recursos educativos completado")