"""
Script Principal de Web Scraping para RAG Académico
Extrae papers, políticas de becas y recursos educativos
"""
import os
import sys
import logging
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio backend-python al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar scrapers
from scrapers.repository_scraper import RepositoryScraper
from scrapers.becas_scraper import BecasScraper
from scrapers.recursos_scraper import RecursosEducativosScraper
from scrapers.scholar_scraper import ScholarScraper


class PapersRecursosManager:
    """Gestiona todo el proceso de scraping"""
    
    def __init__(self, base_path='datos'):
        # Usar ruta relativa al archivo actual
        script_dir = Path(__file__).parent
        self.base_path = script_dir / base_path
        self.papers_dir = self.base_path / 'papers_academicos'
        self.rag_dir = self.base_path / 'rag_knowledge'
        
        # Crear directorios
        self.papers_dir.mkdir(parents=True, exist_ok=True)
        self.rag_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✓ Directorios creados en: {self.base_path}")
    
    def scrape_all(self):
        """Ejecuta todos los scrapers"""
        logger.info("\n" + "="*80)
        logger.info("🚀 INICIANDO WEB SCRAPING PARA RAG ACADÉMICO")
        logger.info("="*80 + "\n")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'scrapers': {}
        }
        
        # 1. Google Scholar / arXiv Papers - Papers académicos
        try:
            logger.info("\n📚 FASE 1: Extrayendo papers académicos de fuentes públicas")
            logger.info("-" * 80)
            
            scholar_scraper = ScholarScraper()
            
            # Consultas más específicas sobre deserción estudiantil
            queries = [
                "student dropout factors higher education",
                "academic retention prediction models",
                "student attrition causes university",
                "dropout prevention strategies education",
                "early intervention student success",
                "student persistence higher education",
                "academic dropout risk factors",
                "student retention strategies university",
                "dropout prediction models education",
                "academic early warning systems"
            ]
            
            papers = scholar_scraper.scrape_multiple_queries(queries, papers_per_query=5)
            
            if papers:
                output_file = self.papers_dir / 'papers_desercion.json'
                scholar_scraper.save_to_json(papers, str(output_file))
                
                results['scrapers']['academic_papers'] = {
                    'status': 'success',
                    'papers_count': len(papers),
                    'output_file': str(output_file)
                }
                
                logger.info(f"✅ Papers académicos completado: {len(papers)} papers extraídos\n")
            else:
                raise Exception("No se pudieron extraer papers de las fuentes públicas")
            
        except Exception as e:
            logger.error(f"❌ Error al extraer papers académicos: {e}")
            results['scrapers']['academic_papers'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 2. Repositorios Institucionales
        try:
            logger.info("\n🏛️ FASE 2: Extrayendo de repositorios ecuatorianos")
            logger.info("-" * 80)
            
            repo_scraper = RepositoryScraper()
            search_terms = [
                "deserción estudiantil",
                "abandono universitario",
                "retención estudiantil"
            ]
            
            documents = repo_scraper.scrape_all_repositories(search_terms)
            output_file = self.papers_dir / 'repositorios_ecuador.txt'
            repo_scraper.save_to_text(documents, str(output_file))
            
            results['scrapers']['repositorios'] = {
                'status': 'success',
                'documents_count': len(documents),
                'output_file': str(output_file)
            }
            
            logger.info(f"✅ Repositorios completado: {len(documents)} documentos\n")
            
        except Exception as e:
            logger.error(f"❌ Error en Repositorios: {e}")
            results['scrapers']['repositorios'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 3. Políticas de Becas
        try:
            logger.info("\n🎓 FASE 3: Extrayendo políticas de becas")
            logger.info("-" * 80)
            
            becas_scraper = BecasScraper(use_selenium=False)
            becas_content = becas_scraper.scrape_all_becas()
            output_file = self.papers_dir / 'politicas_becas.txt'
            becas_scraper.save_to_file(becas_content, str(output_file))
            becas_scraper.close()
            
            results['scrapers']['becas'] = {
                'status': 'success',
                'output_file': str(output_file)
            }
            
            logger.info(f"✅ Becas completado\n")
            
        except Exception as e:
            logger.error(f"❌ Error en Becas: {e}")
            results['scrapers']['becas'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 4. Recursos Educativos
        try:
            logger.info("\n📖 FASE 4: Extrayendo recursos educativos")
            logger.info("-" * 80)
            
            recursos_scraper = RecursosEducativosScraper()
            recursos_content = recursos_scraper.scrape_open_resources()
            output_file = self.papers_dir / 'recursos_orientacion.txt'
            recursos_scraper.save_to_file(recursos_content, str(output_file))
            
            results['scrapers']['recursos'] = {
                'status': 'success',
                'output_file': str(output_file)
            }
            
            logger.info(f"✅ Recursos educativos completado\n")
            
        except Exception as e:
            logger.error(f"❌ Error en Recursos: {e}")
            results['scrapers']['recursos'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Guardar resumen de ejecución
        summary_file = self.papers_dir / 'scraping_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info("\n" + "="*80)
        logger.info("🎉 WEB SCRAPING COMPLETADO")
        logger.info("="*80)
        logger.info(f"\n📊 Resumen guardado en: {summary_file}")
        
        self._print_summary(results)
        
        return results
    
    def _print_summary(self, results):
        """Imprime resumen de resultados"""
        logger.info("\n📋 RESUMEN DE EXTRACCIÓN:")
        logger.info("-" * 80)
        
        for scraper_name, data in results['scrapers'].items():
            status_icon = "✅" if data['status'] == 'success' else "❌"
            logger.info(f"{status_icon} {scraper_name.upper()}: {data['status']}")
            
            if data['status'] == 'success':
                if 'papers_count' in data:
                    logger.info(f"   └─ Papers: {data['papers_count']}")
                if 'documents_count' in data:
                    logger.info(f"   └─ Documentos: {data['documents_count']}")
                logger.info(f"   └─ Archivo: {data['output_file']}")
            else:
                logger.info(f"   └─ Error: {data.get('error', 'Unknown')}")
        
        logger.info("\n" + "="*80)
        logger.info("📁 Archivos generados en:")
        logger.info(f"   • papers_desercion.json")
        logger.info(f"   • repositorios_ecuador.txt")
        logger.info(f"   • politicas_becas.txt")
        logger.info(f"   • recursos_orientacion.txt")
        logger.info("="*80 + "\n")


def main():
    """Función principal"""
    try:
        manager = PapersRecursosManager(base_path='datos')
        results = manager.scrape_all()
        
        # Verificar si hubo éxitos
        success_count = sum(
            1 for data in results['scrapers'].values() 
            if data['status'] == 'success'
        )
        
        if success_count > 0:
            logger.info(f"\n✅ Scraping exitoso: {success_count}/{len(results['scrapers'])} scrapers completados")
            logger.info("\n🔄 Siguiente paso: Ejecutar 'python ingest_scraped_data.py' para ingestar en ChromaDB")
            return 0
        else:
            logger.error("\n❌ No se completó ningún scraper exitosamente")
            return 1
            
    except Exception as e:
        logger.error(f"\n❌ Error fatal: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())