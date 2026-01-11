"""
Módulo de Scrapers para extracción de datos académicos
"""
from .scholar_scraper import ScholarScraper
from .repository_scraper import RepositoryScraper
from .becas_scraper import BecasScraper
from .recursos_scraper import RecursosEducativosScraper

__all__ = [
    'ScholarScraper',
    'RepositoryScraper',
    'BecasScraper',
    'RecursosEducativosScraper'
    
]

__version__ = '1.0.0'