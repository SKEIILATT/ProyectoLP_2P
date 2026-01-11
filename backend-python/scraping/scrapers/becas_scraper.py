"""
Scraper para Políticas de Becas Universitarias Ecuatorianas
"""
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BecasScraper:
    def __init__(self, use_selenium=False):
        """
        Inicializa el scraper
        
        Args:
            use_selenium: Si usar Selenium para páginas dinámicas
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.use_selenium = use_selenium
        self.driver = None
        
        if use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Configura Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("✓ Selenium WebDriver configurado")
    
    def scrape_espol_becas(self) -> str:
        """
        Extrae información sobre becas de ESPOL
        
        Returns:
            Texto con información de becas
        """
        url = "https://www.bienestar.espol.edu.ec/es/becas"
        content = ""
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer título principal
            title = soup.find('h1')
            if title:
                content += f"# {title.text.strip()}\n\n"
            
            # Extraer contenido principal
            main_content = soup.find('div', class_='field-item')
            if not main_content:
                main_content = soup.find('article')
            
            if main_content:
                # Extraer párrafos
                paragraphs = main_content.find_all(['p', 'div', 'ul', 'ol'])
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 20:  # Filtrar textos muy cortos
                        content += f"{text}\n\n"
            
            logger.info("✓ Extraído contenido de ESPOL Becas")
            
        except Exception as e:
            logger.error(f"Error al extraer becas ESPOL: {e}")
            content += f"ERROR: No se pudo acceder a {url}\n\n"
        
        return content
    
    def scrape_senescyt_becas(self) -> str:
        """
        Extrae información sobre becas de SENESCYT
        
        Returns:
            Texto con información de becas
        """
        url = "https://www.educacionsuperior.gob.ec/becas/"
        content = ""
        
        try:
            if self.use_selenium and self.driver:
                self.driver.get(url)
                time.sleep(3)
                
                # Esperar a que cargue el contenido
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            else:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer título
            title = soup.find('h1')
            if title:
                content += f"# {title.text.strip()}\n\n"
            
            # Extraer contenido
            main_content = soup.find('main') or soup.find('article')
            if main_content:
                paragraphs = main_content.find_all(['p', 'div', 'li'])
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 30:
                        content += f"{text}\n\n"
            
            logger.info("✓ Extraído contenido de SENESCYT Becas")
            
        except Exception as e:
            logger.error(f"Error al extraer becas SENESCYT: {e}")
            content += f"ERROR: No se pudo acceder a {url}\n\n"
        
        return content
    
    def scrape_generic_becas(self, url: str, institution_name: str) -> str:
        """
        Scraper genérico para páginas de becas
        
        Args:
            url: URL de la página de becas
            institution_name: Nombre de la institución
            
        Returns:
            Texto extraído
        """
        content = f"# BECAS - {institution_name.upper()}\n\n"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer todo el texto relevante
            for tag in soup.find_all(['p', 'li', 'div', 'span']):
                text = tag.get_text(strip=True)
                if len(text) > 30 and not text.startswith('©'):
                    content += f"{text}\n\n"
            
            logger.info(f"✓ Extraído contenido de {institution_name}")
            
        except Exception as e:
            logger.error(f"Error al extraer {institution_name}: {e}")
            content += f"ERROR: No se pudo acceder a {url}\n\n"
        
        return content
    
    def scrape_all_becas(self) -> str:
        """
        Extrae información de becas de todas las fuentes
        
        Returns:
            Texto consolidado con todas las políticas de becas
        """
        logger.info("\n🎓 Iniciando extracción de políticas de becas...")
        
        all_content = "# POLÍTICAS DE BECAS Y AYUDAS ECONÓMICAS - ECUADOR\n\n"
        all_content += "=" * 80 + "\n\n"
        
        # ESPOL
        logger.info("\n📚 Extrayendo becas ESPOL...")
        espol_content = self.scrape_espol_becas()
        all_content += espol_content + "\n" + "=" * 80 + "\n\n"
        time.sleep(2)
        
        # SENESCYT
        logger.info("\n🏛️ Extrayendo becas SENESCYT...")
        senescyt_content = self.scrape_senescyt_becas()
        all_content += senescyt_content + "\n" + "=" * 80 + "\n\n"
        time.sleep(2)
        
        # Otras universidades
        other_universities = [
            ("https://repositorio.uce.edu.ec/archivos/DBU/2024/BECAS_ESTUDIANTILES/Reglamento_de_Becas_para_Estudiantes_de_Tercer_Nivel.pdf", "UCE"),
            ("https://www.puce.edu.ec/financiamiento-y-becas/becas/", "PUCE"),
        ]
        
        for url, name in other_universities:
            logger.info(f"\n🏫 Extrayendo becas {name}...")
            try:
                content = self.scrape_generic_becas(url, name)
                all_content += content + "\n" + "=" * 80 + "\n\n"
                time.sleep(2)
            except Exception as e:
                logger.warning(f"No se pudo extraer {name}: {e}")
        
        logger.info("\n✅ Extracción de becas completada")
        return all_content
    
    def save_to_file(self, content: str, filepath: str):
        """Guarda el contenido en un archivo"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"💾 Guardado en: {filepath}")
    
    def close(self):
        """Cierra el driver de Selenium si está abierto"""
        if self.driver:
            self.driver.quit()
            logger.info("✓ Selenium WebDriver cerrado")


# Script de ejecución
if __name__ == "__main__":
    
    scraper = BecasScraper(use_selenium=False)
    
    try:
        # Extraer todas las políticas de becas
        becas_content = scraper.scrape_all_becas()
        
        # Guardar resultado
        import os
        os.makedirs('datos/papers_academicos', exist_ok=True)
        scraper.save_to_file(becas_content, 'datos/papers_academicos/politicas_becas.txt')
        
        print("\n🎉 Scraping de becas completado")
        
    finally:
        scraper.close()