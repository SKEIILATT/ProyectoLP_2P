"""
Scraper para Repositorios Institucionales Ecuatorianos
"""
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RepositoryScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
    
    def scrape_espol_dspace(self, search_term: str, max_results: int = 10) -> List[Dict]:
        base_url = "http://www.dspace.espol.edu.ec"
        search_url = f"{base_url}/simple-search"

        documents = []

        try:
            params = {
                'query': search_term,
                'sort_by': 'score',
                'order': 'desc'
            }

            response = self.session.get(search_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar resultados de búsqueda - estructura actualizada
            result_container = soup.find('div', class_='discovery-result-results')

            if result_container:
                # Buscar filas de resultados
                rows = result_container.find_all('tr')  # Las filas de la tabla

                for idx, row in enumerate(rows[1:max_results+1]):  # Saltar header, tomar max_results
                    try:
                        # Extraer celdas de la fila
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            # Fecha, Título, Autor
                            date = cells[0].text.strip() if cells[0] else 'N/A'
                            title_elem = cells[1].find('a')
                            title = title_elem.text.strip() if title_elem else cells[1].text.strip()
                            url = base_url + title_elem.get('href', '') if title_elem else 'N/A'

                            authors = cells[2].text.strip() if len(cells) > 2 else 'N/A'

                            doc_data = {
                                'title': title,
                                'authors': [authors] if authors != 'N/A' else [],
                                'date': date,
                                'abstract': 'N/A',  
                                'url': url,
                                'source': 'ESPOL DSpace',
                                'search_term': search_term
                            }

                            documents.append(doc_data)
                            logger.info(f"✓ ESPOL: {title[:50]}...")

                    except Exception as e:
                        logger.warning(f"Error al procesar fila {idx}: {e}")
                        continue

            time.sleep(1)

        except Exception as e:
            logger.error(f"Error en ESPOL DSpace: {e}")

        return documents
    
    def scrape_generic_repository(self, base_url: str, search_path: str, 
                                  search_term: str, max_results: int = 5) -> List[Dict]:
        """
        Scraper genérico para otros repositorios institucionales
        
        Args:
            base_url: URL base del repositorio
            search_path: Ruta de búsqueda
            search_term: Término a buscar
            max_results: Máximo de resultados
            
        Returns:
            Lista de documentos
        """
        documents = []
        
        try:
            search_url = f"{base_url}{search_path}"
            params = {'q': search_term}
            
            response = self.session.get(search_url, params=params, 
                                       headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar links de documentos
            links = soup.find_all('a', href=re.compile(r'handle|item|record'))
            
            for idx, link in enumerate(links[:max_results]):
                try:
                    title = link.text.strip()
                    url = link.get('href', '')
                    
                    if not url.startswith('http'):
                        url = base_url + url
                    
                    doc_data = {
                        'title': title,
                        'url': url,
                        'source': base_url,
                        'search_term': search_term
                    }
                    
                    documents.append(doc_data)
                    logger.info(f"✓ Repositorio: {title[:50]}...")
                    
                except Exception as e:
                    logger.warning(f"Error al procesar link {idx}: {e}")
                    continue
            
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error al buscar en {base_url}: {e}")
        
        return documents
    
    def scrape_all_repositories(self, search_terms: List[str]) -> List[Dict]:
        """
        Busca en múltiples repositorios ecuatorianos
        
        Args:
            search_terms: Lista de términos de búsqueda
            
        Returns:
            Lista consolidada de documentos
        """
        all_documents = []
        
        # Repositorios a consultar
        repositories = [
            ('ESPOL', 'http://www.dspace.espol.edu.ec', '/simple-search'),
            
        ]
        
        for search_term in search_terms:
            logger.info(f"\n🔍 Buscando: '{search_term}'")
            
            # ESPOL DSpace (scraper específico)
            espol_docs = self.scrape_espol_dspace(search_term, max_results=5)
            all_documents.extend(espol_docs)
            
            time.sleep(3)
        
        logger.info(f"\n✅ Total documentos de repositorios: {len(all_documents)}")
        return all_documents
    
    def save_to_text(self, documents: List[Dict], filepath: str):
        """Guarda documentos en formato texto para RAG"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# DOCUMENTOS DE REPOSITORIOS INSTITUCIONALES ECUATORIANOS\n\n")
            
            for idx, doc in enumerate(documents, 1):
                f.write(f"## DOCUMENTO {idx}: {doc['title']}\n\n")
                f.write(f"**Fuente:** {doc['source']}\n")
                f.write(f"**URL:** {doc['url']}\n")
                
                if doc.get('authors'):
                    f.write(f"**Autores:** {', '.join(doc['authors'])}\n")
                if doc.get('date'):
                    f.write(f"**Fecha:** {doc['date']}\n")
                
                if doc.get('abstract') and doc['abstract'] != 'N/A':
                    f.write(f"\n**Resumen:**\n{doc['abstract']}\n")
                
                f.write("\n" + "="*80 + "\n\n")
        
        logger.info(f"💾 Guardado en: {filepath}")

# Script de ejecución
if __name__ == "__main__":
    scraper = RepositoryScraper()
    
    search_terms = [
        "deserción estudiantil",
        "abandono universitario",
        "retención estudiantil"
    ]
    
    documents = scraper.scrape_all_repositories(search_terms)
    
    import os
    os.makedirs('datos/papers_academicos', exist_ok=True)
    print(documents)
    scraper.save_to_text(documents, 'datos/papers_academicos/repositorios_ecuador.txt')
    
    print(f"\n🎉 Scraping completado: {len(documents)} documentos extraídos")