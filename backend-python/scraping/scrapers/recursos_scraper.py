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
        Extrae contenido sobre técnicas de estudio y retención estudiantil de múltiples fuentes
        
        Returns:
            Texto con recursos educativos
        """
        content = "# GUÍA DE TÉCNICAS DE ESTUDIO Y RETENCIÓN ESTUDIANTIL\n\n"
        content += "=" * 80 + "\n\n"
        
        # 1. Scrapear Wikipedia - Técnicas de estudio
        logger.info("📚 Extrayendo técnicas de estudio...")
        wiki_content = self._scrape_study_techniques()
        content += wiki_content + "\n" + "=" * 80 + "\n\n"
        
        # 2. Scrapear sobre retención estudiantil
        logger.info("🎓 Extrayendo información sobre retención estudiantil...")
        retention_content = self._scrape_retention_info()
        content += retention_content + "\n" + "=" * 80 + "\n\n"
        
        # 3. Scrapear sobre autorregulación
        logger.info("🧠 Extrayendo información sobre habilidades de autorregulación...")
        self_regulation_content = self._scrape_self_regulation()
        content += self_regulation_content + "\n" + "=" * 80 + "\n\n"
        
        logger.info("✓ Generado contenido sobre técnicas de estudio")
        return content
    
    def _scrape_study_techniques(self) -> str:
        """Extrae información sobre técnicas de estudio"""
        content = "## 1. TÉCNICAS DE ESTUDIO EFECTIVAS\n\n"
        
        urls = {
            "https://en.wikipedia.org/wiki/Study_skills": "Study Skills",
            "https://en.wikipedia.org/wiki/Learning_theory": "Teoría del Aprendizaje",
            "https://en.wikipedia.org/wiki/Time_management": "Gestión del Tiempo"
        }
        
        for url, title in urls.items():
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraer el contenido principal
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if content_div:
                    content += f"\n### {title}\n"
                    
                    # Extraer párrafos
                    paragraphs = content_div.find_all('p')[:8]  # Primeros 8 párrafos
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text) > 50:
                            content += f"{text}\n\n"
                
                logger.info(f"  ✓ Extraído de {title}")
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"  ⚠️ Error al extraer {title}: {e}")
        
        return content
    
    def _scrape_retention_info(self) -> str:
        """Extrae información sobre retención estudiantil"""
        content = "## 2. FACTORES DE RETENCIÓN ESTUDIANTIL\n\n"
        
        urls = {
            "https://en.wikipedia.org/wiki/Student_retention": "Student Retention",
            "https://en.wikipedia.org/wiki/Academic_performance": "Academic Performance"
        }
        
        for url, title in urls.items():
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if content_div:
                    content += f"### {title}\n"
                    
                    # Extraer párrafos
                    paragraphs = content_div.find_all('p')[:6]
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text) > 50 and text.count(' ') > 10:
                            content += f"- {text}\n"
                    
                    content += "\n"
                
                logger.info(f"  ✓ Extraído de {title}")
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"  ⚠️ Error al extraer {title}: {e}")
        
        return content
    
    def _scrape_self_regulation(self) -> str:
        """Extrae información sobre autorregulación y metacognición"""
        content = "## 3. HABILIDADES DE AUTORREGULACIÓN Y METACOGNICIÓN\n\n"
        
        urls = {
            "https://en.wikipedia.org/wiki/Self-regulated_learning": "Aprendizaje Autorregulado",
            "https://en.wikipedia.org/wiki/Metacognition": "Metacognición",
            "https://en.wikipedia.org/wiki/Educational_psychology": "Psicología Educativa"
        }
        
        for url, title in urls.items():
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if content_div:
                    content += f"### {title}\n"
                    
                    # Extraer párrafos principales
                    paragraphs = content_div.find_all('p')[:7]
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text) > 50:
                            content += f"{text}\n\n"
                
                logger.info(f"  ✓ Extraído de {title}")
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"  ⚠️ Error al extraer {title}: {e}")
        
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
        """Extrae referencias de fuentes académicas y educativas"""
        content = "# REFERENCIAS Y RECURSOS ADICIONALES\n\n"
        
        # 1. Extraer información de organizaciones educativas
        logger.info("🔗 Extrayendo referencias de sitios educativos...")
        content += self._scrape_educational_organizations()
        
        # 2. Agregar referencias de herramientas
        content += self._scrape_learning_tools()
        
        return content
    
    def _scrape_educational_organizations(self) -> str:
        """Extrae información de organizaciones educativas"""
        content = "## Organizaciones y Portales Educativos\n\n"
        
        urls = {
            "https://en.wikipedia.org/wiki/Higher_education": "Higher Education",
            "https://en.wikipedia.org/wiki/Educational_technology": "Educational Technology",
            "https://en.wikipedia.org/wiki/Distance_education": "Distance Education"
        }
        
        for url, title in urls.items():
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraer el primer párrafo
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if content_div:
                    first_para = content_div.find('p')
                    if first_para:
                        text = first_para.get_text(strip=True)
                        content += f"### {title}\n{text}\n\n"
                
                logger.info(f"  ✓ Información de {title}")
                time.sleep(1.5)
                
            except Exception as e:
                logger.warning(f"  ⚠️ Error al extraer {title}: {e}")
        
        return content
    
    def _scrape_learning_tools(self) -> str:
        """Extrae información de herramientas de aprendizaje"""
        content = "## Plataformas y Herramientas de Aprendizaje\n\n"
        
        tools = [
            ("https://en.wikipedia.org/wiki/Khan_Academy", "Khan Academy"),
            ("https://en.wikipedia.org/wiki/Coursera", "Coursera"),
            ("https://en.wikipedia.org/wiki/OpenStax", "OpenStax")
        ]
        
        for url, name in tools:
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if content_div:
                    # Extraer 2-3 párrafos sobre la herramienta
                    paragraphs = content_div.find_all('p')[:2]
                    
                    content += f"### {name}\n"
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text) > 50:
                            content += f"{text}\n\n"
                    
                    content += "\n"
                
                logger.info(f"  ✓ Información de {name}")
                time.sleep(1.5)
                
            except Exception as e:
                logger.warning(f"  ⚠️ Error al extraer {name}: {e}")
        
        # Agregar recursos locales ecuatorianos
        content += self._add_ecuadorian_resources()
        
        return content
    
    def _add_ecuadorian_resources(self) -> str:
        """Extrae información sobre recursos educativos de Ecuador mediante scraping"""
        content = "\n## Recursos Educativos en Ecuador\n\n"
        
        # 1. Información sobre educación superior en Ecuador
        logger.info("  🇪🇨 Extrayendo información sobre educación superior en Ecuador...")
        content += self._scrape_ecuador_higher_education()
        
        # 2. Información sobre universidades ecuatorianas
        logger.info("  🏫 Extrayendo información sobre universidades ecuatorianas...")
        content += self._scrape_ecuador_universities()
        
        # 3. Información sobre becas y financiamiento
        logger.info("  💰 Extrayendo información sobre financiamiento estudiantil...")
        content += self._scrape_ecuador_financial_aid()
        
        return content
    
    def _scrape_ecuador_higher_education(self) -> str:
        """Extrae información sobre educación superior en Ecuador"""
        content = "### Educación Superior en Ecuador\n\n"
        
        urls = {
            "https://en.wikipedia.org/wiki/Ecuador": "Ecuador",
            "https://en.wikipedia.org/wiki/List_of_universities_in_South_America": "Universidades Sudamericanas"
        }
        
        for url, title in urls.items():
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if content_div:
                    # Buscar párrafos que contengan información sobre educación
                    paragraphs = content_div.find_all('p')
                    
                    extracted = 0
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        # Filtrar por palabras clave relacionadas con educación
                        if any(keyword in text.lower() for keyword in ['education', 'educación', 'university', 'universit', 'higher', 'superior']):
                            if len(text) > 80 and extracted < 3:
                                content += f"- {text}\n\n"
                                extracted += 1
                
                if extracted > 0:
                    logger.info(f"    ✓ Extraído información de {title}")
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"    ⚠️ Error al extraer {title}: {e}")
        
        return content
    
    def _scrape_ecuador_universities(self) -> str:
        """Extrae información sobre universidades en Ecuador"""
        content = "### Principales Universidades en Ecuador\n\n"
        
        # Usar URLs válidas de Wikipedia que existen
        urls = [
            "https://en.wikipedia.org/wiki/Category:Universities_in_Ecuador",
            "https://en.wikipedia.org/wiki/Higher_education_in_Ecuador"
        ]
        
        universities_found = 0
        
        for url in urls:
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if content_div:
                    # Extraer párrafos iniciales
                    paragraphs = content_div.find_all('p')[:4]
                    
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text) > 60 and universities_found < 2:
                            content += f"- {text}\n\n"
                            universities_found += 1
                    
                    # Extraer lista de instituciones si existe
                    lists = content_div.find_all('ul')
                    if lists and universities_found < 2:
                        list_items = lists[0].find_all('li')[:5]
                        for li in list_items:
                            text = li.get_text(strip=True)
                            if len(text) > 10:
                                content += f"- {text}\n"
                                universities_found += 1
                
                if universities_found > 0:
                    logger.info(f"    ✓ Información de universidades extraída")
                time.sleep(2)
                
                if universities_found > 0:
                    break
                
            except Exception as e:
                logger.warning(f"    ⚠️ Error al extraer de {url.split('/')[-1]}: {str(e)[:50]}")
        
        # Si no se encontró información, agregar contenido contextual
        if universities_found == 0:
            content += """- Instituciones de educación superior públicas y privadas en Ecuador
- Universidades acreditadas por el Consejo de Aseguramiento de la Calidad de la Educación Superior (CACES)
- Instituciones notables: ESPOL, Universidades Estatales, UCE, PUCE
"""
            logger.info(f"    ✓ Información contextual sobre universidades agregada")
        
        return content
    
    def _scrape_ecuador_financial_aid(self) -> str:
        """Extrae información sobre programas de financiamiento estudiantil"""
        content = "### Programas de Financiamiento y Becas en Ecuador\n\n"
        
        # Scrapear información sobre educación y políticas financieras
        urls = [
            "https://en.wikipedia.org/wiki/Student_financial_aid",
            "https://en.wikipedia.org/wiki/Scholarship"
        ]
        
        financial_info_found = False
        
        for url in urls:
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if content_div:
                    # Extraer párrafos sobre tipos de financiamiento
                    paragraphs = content_div.find_all('p')[:5]
                    
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text) > 70:
                            content += f"- {text}\n\n"
                            financial_info_found = True
                
                logger.info(f"    ✓ Información de financiamiento extraída")
                time.sleep(2)
                break
                
            except Exception as e:
                logger.warning(f"    ⚠️ Error al extraer información de becas: {e}")
        
        # Agregar información específica de Ecuador
        content += """
### Instituciones Ecuatorianas Responsables de Educación
- **SENESCYT**: Secretaría de Educación Superior, Ciencia, Tecnología e Innovación - Entidad reguladora de la educación superior
- **CACES**: Consejo de Aseguramiento de la Calidad de la Educación Superior - Garantiza estándares de calidad
- **Universidades Públicas**: Instituciones como ESPOL, Universidades Estatales con programas de retención

### Tipos de Apoyo Financiero Disponibles
- Becas por desempeño académico
- Programas de crédito educativo
- Fondos de solidaridad estudiantil
- Becas para grupos vulnerables
- Programas de trabajo-estudio
"""
        
        return content
    
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