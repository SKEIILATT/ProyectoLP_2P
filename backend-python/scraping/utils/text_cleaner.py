"""
Utilidades para limpieza y procesamiento de texto
"""
import re
from typing import List


class TextCleaner:
    """Limpia y procesa texto extraído del web scraping"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Limpia texto general
        
        Args:
            text: Texto a limpiar
            
        Returns:
            Texto limpio
        """
        if not text:
            return ""
        
        # Eliminar múltiples espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar múltiples saltos de línea
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Eliminar espacios al inicio y final
        text = text.strip()
        
        return text
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """
        Elimina tags HTML del texto
        
        Args:
            text: Texto con HTML
            
        Returns:
            Texto sin HTML
        """
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    @staticmethod
    def remove_special_chars(text: str, keep_punctuation=True) -> str:
        """
        Elimina caracteres especiales
        
        Args:
            text: Texto a limpiar
            keep_punctuation: Si mantener puntuación básica
            
        Returns:
            Texto limpio
        """
        if keep_punctuation:
            # Mantener letras, números, espacios y puntuación básica
            pattern = r'[^a-zA-Z0-9áéíóúñÑ\s.,;:!?¿¡()\-]'
        else:
            # Solo letras, números y espacios
            pattern = r'[^a-zA-Z0-9áéíóúñÑ\s]'
        
        return re.sub(pattern, '', text)
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normaliza espacios en blanco
        
        Args:
            text: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        # Reemplazar tabs por espacios
        text = text.replace('\t', ' ')
        
        # Reemplazar múltiples espacios por uno solo
        text = re.sub(r' +', ' ', text)
        
        # Normalizar saltos de línea
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    @staticmethod
    def extract_abstract(text: str) -> str:
        """
        Intenta extraer el abstract de un texto académico
        
        Args:
            text: Texto del paper
            
        Returns:
            Abstract extraído o string vacío
        """
        # Patrones comunes para abstracts
        patterns = [
            r'abstract[:\s]+(.*?)(?:introduction|keywords|1\.|índice)',
            r'resumen[:\s]+(.*?)(?:introducción|palabras clave|1\.|abstract)',
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """
        Divide texto en oraciones
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de oraciones
        """
        # Patrones de fin de oración
        sentence_endings = r'[.!?]+[\s\n]+'
        
        sentences = re.split(sentence_endings, text)
        
        # Limpiar y filtrar oraciones vacías
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 500, add_ellipsis=True) -> str:
        """
        Trunca texto a una longitud máxima
        
        Args:
            text: Texto a truncar
            max_length: Longitud máxima
            add_ellipsis: Si agregar '...' al final
            
        Returns:
            Texto truncado
        """
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length].rsplit(' ', 1)[0]
        
        if add_ellipsis:
            truncated += '...'
        
        return truncated
    
    @staticmethod
    def clean_paper_metadata(paper_dict: dict) -> dict:
        """
        Limpia metadata de un paper
        
        Args:
            paper_dict: Diccionario con metadata del paper
            
        Returns:
            Diccionario limpio
        """
        cleaned = {}
        
        # Limpiar título
        if 'title' in paper_dict:
            cleaned['title'] = TextCleaner.clean_text(paper_dict['title'])
        
        # Limpiar abstract
        if 'abstract' in paper_dict:
            abstract = TextCleaner.clean_text(paper_dict['abstract'])
            cleaned['abstract'] = TextCleaner.remove_html_tags(abstract)
        
        # Limpiar autores
        if 'authors' in paper_dict:
            if isinstance(paper_dict['authors'], list):
                cleaned['authors'] = [
                    TextCleaner.clean_text(author) 
                    for author in paper_dict['authors']
                ]
            else:
                cleaned['authors'] = [TextCleaner.clean_text(str(paper_dict['authors']))]
        
        # Copiar otros campos sin modificar
        for key in ['year', 'citations', 'url', 'venue', 'query']:
            if key in paper_dict:
                cleaned[key] = paper_dict[key]
        
        return cleaned


# Ejemplo de uso
if __name__ == "__main__":
    cleaner = TextCleaner()
    
    # Texto de ejemplo
    sample_text = """
    <p>Este es un    texto con    espacios    múltiples.</p>
    
    
    Y con saltos de línea innecesarios.
    """
    
    print("Original:")
    print(repr(sample_text))
    print("\nLimpio:")
    print(repr(cleaner.clean_text(cleaner.remove_html_tags(sample_text))))