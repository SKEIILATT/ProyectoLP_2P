"""
Scraper para Papers Académicos - Usando fuentes públicas confiables
Extrae información de arXiv, PubMed y otras fuentes de papers académicos
"""
import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScholarScraper:
    def __init__(self):
        """Inicializa el scraper con headers realistas"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
    
    def search_arxiv_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Busca papers en arXiv (fuente pública y confiable)
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de diccionarios con metadata de papers
        """
        papers = []
        try:
            # API de arXiv - no requiere autenticación ni tiene CAPTCHA
            url = "http://export.arxiv.org/api/query?"
            search_query = f"search_query=all:{query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
            
            response = self.session.get(url + search_query, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parsear XML de arXiv
            soup = BeautifulSoup(response.content, 'xml')
            entries = soup.find_all('entry')
            
            for entry in entries:
                try:
                    # Extraer información del paper
                    title = entry.find('title')
                    authors = entry.find_all('author')
                    summary = entry.find('summary')
                    published = entry.find('published')
                    arxiv_id = entry.find('id')
                    
                    paper_data = {
                        'title': title.text.strip() if title else 'N/A',
                        'abstract': summary.text.strip() if summary else 'N/A',
                        'year': published.text[:4] if published else 'N/A',
                        'authors': [a.find('name').text for a in authors] if authors else [],
                        'citations': 0,
                        'url': arxiv_id.text if arxiv_id else 'N/A',
                        'venue': 'arXiv',
                        'query': query
                    }
                    
                    papers.append(paper_data)
                    logger.info(f"✓ Extraído (arXiv): {paper_data['title'][:50]}...")
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Error al procesar entry: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error en búsqueda arXiv '{query}': {e}")
        
        return papers
    
    def search_pubmed_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Busca papers en PubMed (medicina y ciencias de la salud)
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de diccionarios con metadata de papers
        """
        papers = []
        try:
            # API de PubMed - pública y sin CAPTCHA
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'rettype': 'json'
            }
            
            response = self.session.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            try:
                data = response.json()
            except:
                logger.warning(f"No se pudo parsear respuesta JSON de PubMed para '{query}'")
                return papers
            
            pubmed_ids = data.get('esearchresult', {}).get('idlist', [])
            
            if not pubmed_ids:
                logger.info(f"No se encontraron resultados en PubMed para '{query}'")
                return papers
            
            for pmid in pubmed_ids[:max_results]:
                try:
                    # Obtener detalles del paper
                    detail_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                    detail_params = {
                        'db': 'pubmed',
                        'id': pmid,
                        'rettype': 'json'
                    }
                    
                    detail_response = self.session.get(detail_url, params=detail_params, timeout=10)
                    detail_response.raise_for_status()
                    
                    try:
                        detail_data = detail_response.json()
                    except:
                        continue
                    
                    article = detail_data.get('result', {}).get(str(pmid), {})
                    
                    if not article:
                        continue
                    
                    paper_data = {
                        'title': article.get('title', 'N/A'),
                        'abstract': article.get('abstract', 'N/A'),
                        'year': article.get('pubdate', 'N/A')[:4] if article.get('pubdate') else 'N/A',
                        'authors': article.get('authors', []),
                        'citations': 0,
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        'venue': 'PubMed',
                        'query': query
                    }
                    
                    papers.append(paper_data)
                    logger.info(f"✓ Extraído (PubMed): {paper_data['title'][:50]}...")
                    time.sleep(1)
                    
                except Exception as e:
                    logger.debug(f"Error al procesar PubMed {pmid}: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"Error en búsqueda PubMed '{query}': {e}")
        
        return papers
    
    def search_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Búsqueda combinada en múltiples fuentes
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados por fuente
            
        Returns:
            Lista de diccionarios con metadata de papers
        """
        papers = []
        
        # Buscar en arXiv
        arxiv_papers = self.search_arxiv_papers(query, max(3, max_results // 2))
        papers.extend(arxiv_papers)
        time.sleep(2)
        
        # Buscar en PubMed
        pubmed_papers = self.search_pubmed_papers(query, max(2, max_results // 3))
        papers.extend(pubmed_papers)
        time.sleep(2)
        
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
            time.sleep(3)
        
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
    from pathlib import Path
    
    scraper = ScholarScraper()
    
    # Consultas específicas sobre deserción estudiantil
    queries = [
        "student dropout prediction machine learning",
        "education retention student completion",
        "educational data mining dropout detection",
        "student attrition higher education",
        "early warning systems academic performance"
    ]
    
    # Extraer papers
    papers = scraper.scrape_multiple_queries(queries, papers_per_query=5)
    
    # Guardar resultados en la ruta correcta
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / 'datos' / 'papers_academicos'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scraper.save_to_json(papers, str(output_dir / 'papers_desercion.json'))
    
    print(f"\n🎉 Scraping completado: {len(papers)} papers extraídos")