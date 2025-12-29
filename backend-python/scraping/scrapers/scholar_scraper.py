"""
Scraper para Google Scholar - Papers sobre deserción estudiantil
"""
import time
import json
from scholarly import scholarly, ProxyGenerator
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScholarScraper:
    def __init__(self, use_proxy=False):
        """Inicializa el scraper con opción de proxy para evitar bloqueos"""
        if use_proxy:
            pg = ProxyGenerator()
            pg.FreeProxies()
            scholarly.use_proxy(pg)
    
    def search_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Busca papers en Google Scholar
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de diccionarios con metadata de papers
        """
        papers = []
        try:
            search_query = scholarly.search_pubs(query)
            
            for i, result in enumerate(search_query):
                if i >= max_results:
                    break
                
                try:
                    # Extraer información del paper
                    paper_data = {
                        'title': result.get('bib', {}).get('title', 'N/A'),
                        'abstract': result.get('bib', {}).get('abstract', 'N/A'),
                        'year': result.get('bib', {}).get('pub_year', 'N/A'),
                        'authors': result.get('bib', {}).get('author', []),
                        'citations': result.get('num_citations', 0),
                        'url': result.get('pub_url', 'N/A'),
                        'venue': result.get('bib', {}).get('venue', 'N/A'),
                        'query': query
                    }
                    
                    papers.append(paper_data)
                    logger.info(f"✓ Extraído: {paper_data['title'][:50]}...")
                    
                    # Pausa para evitar bloqueos
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Error al procesar paper {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error en búsqueda '{query}': {e}")
        
        return papers
    
    def scrape_multiple_queries(self, queries: List[str], papers_per_query: int = 7) -> List[Dict]:
        """
        Realiza múltiples búsquedas y combina resultados
        
        Args:
            queries: Lista de términos de búsqueda
            papers_per_query: Papers a extraer por consulta
            
        Returns:
            Lista consolidada de papers
        """
        all_papers = []
        
        for query in queries:
            logger.info(f"\n🔍 Buscando: '{query}'")
            papers = self.search_papers(query, papers_per_query)
            all_papers.extend(papers)
            
            # Pausa entre consultas
            time.sleep(5)
        
        # Eliminar duplicados por título
        unique_papers = []
        seen_titles = set()
        
        for paper in all_papers:
            title = paper['title'].lower()
            if title not in seen_titles and title != 'n/a':
                seen_titles.add(title)
                unique_papers.append(paper)
        
        logger.info(f"\n✅ Total de papers únicos: {len(unique_papers)}")
        return unique_papers
    
    def save_to_json(self, papers: List[Dict], filepath: str):
        """Guarda papers en formato JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Guardado en: {filepath}")


# Script de ejecución
if __name__ == "__main__":
    scraper = ScholarScraper(use_proxy=False)
    
    # Consultas específicas sobre deserción estudiantil
    queries = [
        "student dropout prediction machine learning",
        "deserción estudiantil predicción",
        "educational data mining retention",
        "student attrition factors higher education",
        "early warning systems student dropout"
    ]
    
    # Extraer papers
    papers = scraper.scrape_multiple_queries(queries, papers_per_query=5)
    
    # Guardar resultados
    import os
    os.makedirs('datos/papers_academicos', exist_ok=True)
    scraper.save_to_json(papers, 'datos/papers_academicos/papers_desercion.json')
    
    print(f"\n🎉 Scraping completado: {len(papers)} papers extraídos")