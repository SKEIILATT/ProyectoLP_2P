"""
Scraper alternativo usando SerpAPI
Requiere API key gratuita: https://serpapi.com/ (100 búsquedas gratis/mes)
"""
import os
import time
import json
import logging
from typing import List, Dict
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SerpAPIScholarScraper:
    """Scraper de Google Scholar usando SerpAPI"""
    
    def __init__(self, api_key=None):
        """
        Inicializa el scraper
        
        Args:
            api_key: Clave API de SerpAPI (obtener en https://serpapi.com)
        """
        self.api_key = api_key or os.getenv('SERPAPI_KEY')
        self.base_url = "https://serpapi.com/search"
        
        if not self.api_key:
            logger.warning("⚠️  No se proporcionó API key de SerpAPI")
            logger.warning("   Registrate gratis en https://serpapi.com (100 búsquedas/mes)")
    
    def search_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Busca papers usando SerpAPI
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de papers
        """
        if not self.api_key:
            logger.error("❌ No hay API key configurada")
            return []
        
        papers = []
        
        try:
            params = {
                'engine': 'google_scholar',
                'q': query,
                'api_key': self.api_key,
                'num': min(max_results, 20)
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'organic_results' not in data:
                logger.warning(f"No se encontraron resultados para: {query}")
                return []
            
            for result in data['organic_results'][:max_results]:
                paper_data = {
                    'title': result.get('title', 'N/A'),
                    'abstract': result.get('snippet', 'N/A'),
                    'year': self._extract_year(result.get('publication_info', {})),
                    'authors': self._extract_authors(result.get('publication_info', {})),
                    'citations': result.get('inline_links', {}).get('cited_by', {}).get('total', 0),
                    'url': result.get('link', 'N/A'),
                    'venue': self._extract_venue(result.get('publication_info', {})),
                    'query': query
                }
                
                papers.append(paper_data)
                logger.info(f"✓ Extraído: {paper_data['title'][:50]}...")
            
            time.sleep(1)  # Rate limiting
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {e}")
        except Exception as e:
            logger.error(f"Error al buscar '{query}': {e}")
        
        return papers
    
    def _extract_year(self, pub_info: dict) -> str:
        """Extrae año de publicación"""
        summary = pub_info.get('summary', '')
        # Buscar año en formato YYYY
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', summary)
        return year_match.group(0) if year_match else 'N/A'
    
    def _extract_authors(self, pub_info: dict) -> List[str]:
        """Extrae lista de autores"""
        authors_str = pub_info.get('authors', '')
        if authors_str:
            return [a.strip() for a in authors_str.split(',')]
        return []
    
    def _extract_venue(self, pub_info: dict) -> str:
        """Extrae venue/journal"""
        summary = pub_info.get('summary', 'N/A')
        # Remover año si existe
        import re
        venue = re.sub(r'\b(19|20)\d{2}\b', '', summary).strip(' -,')
        return venue if venue else 'N/A'
    
    def scrape_multiple_queries(self, queries: List[str], papers_per_query: int = 7) -> List[Dict]:
        """
        Realiza múltiples búsquedas
        
        Args:
            queries: Lista de términos
            papers_per_query: Papers por consulta
            
        Returns:
            Lista consolidada
        """
        all_papers = []
        
        for query in queries:
            logger.info(f"\n🔍 Buscando: '{query}'")
            papers = self.search_papers(query, papers_per_query)
            all_papers.extend(papers)
            time.sleep(2)
        
        # Eliminar duplicados
        unique_papers = []
        seen_titles = set()
        
        for paper in all_papers:
            title = paper['title'].lower()
            if title not in seen_titles and title != 'n/a':
                seen_titles.add(title)
                unique_papers.append(paper)
        
        logger.info(f"\n✅ Total papers únicos: {len(unique_papers)}")
        return unique_papers
    
    def save_to_json(self, papers: List[Dict], filepath: str):
        """Guarda papers en JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Guardado en: {filepath}")


# Script de prueba
if __name__ == "__main__":
    # Configurar API key
    api_key = input("Ingresa tu API key de SerpAPI (o presiona Enter para saltar): ").strip()
    
    if not api_key:
        print("\n⚠️  Sin API key.")
        
    else:
        scraper = SerpAPIScholarScraper(api_key=api_key)
        
        queries = [
            "student dropout prediction machine learning",
            "deserción estudiantil predicción"
        ]
        
        papers = scraper.scrape_multiple_queries(queries, papers_per_query=5)
        
        import os
        os.makedirs('datos/papers_academicos', exist_ok=True)
        scraper.save_to_json(papers, 'datos/papers_academicos/papers_desercion.json')
        
        print(f"\n🎉 {len(papers)} papers extraídos con SerpAPI")