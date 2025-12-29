"""
Script de Ingesta de Datos Scraped a ChromaDB
Procesa y almacena papers y recursos en la base de conocimiento RAG
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScrapedDataIngestor:
    """Gestiona la ingesta de datos scraped a ChromaDB"""
    
    def __init__(self, 
                 papers_dir='datos/papers_academicos',
                 chroma_dir='datos/chromadb',
                 collection_name='knowledge_base'):
        """
        Inicializa el ingestor
        
        Args:
            papers_dir: Directorio con datos scraped
            chroma_dir: Directorio de ChromaDB
            collection_name: Nombre de la colección
        """
        self.papers_dir = Path(papers_dir)
        self.chroma_dir = Path(chroma_dir)
        self.collection_name = collection_name
        
        # Crear directorio de ChromaDB
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Crear o obtener colección
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Knowledge base for student dropout RAG system"}
        )
        
        # Configurar text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        logger.info(f"✓ ChromaDB inicializado: {self.chroma_dir}")
        logger.info(f"✓ Colección: {self.collection_name}")
    
    def ingest_papers_json(self, filepath: str) -> int:
        """
        Ingesta papers desde archivo JSON
        
        Args:
            filepath: Ruta al archivo JSON con papers
            
        Returns:
            Número de documentos ingestados
        """
        logger.info(f"\n📚 Ingiriendo papers desde: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            
            documents = []
            for i, paper in enumerate(papers):
                # Crear contenido del documento
                content = f"""
Título: {paper.get('title', 'N/A')}

Autores: {', '.join(paper.get('authors', []))}

Año: {paper.get('year', 'N/A')}

Resumen: {paper.get('abstract', 'N/A')}

Citas: {paper.get('citations', 0)}

Venue: {paper.get('venue', 'N/A')}

URL: {paper.get('url', 'N/A')}
"""
                
                # Crear documento con metadata
                doc = Document(
                    page_content=content,
                    metadata={
                        'source': 'google_scholar',
                        'type': 'academic_paper',
                        'title': paper.get('title', 'N/A'),
                        'year': str(paper.get('year', 'N/A')),
                        'citations': paper.get('citations', 0),
                        'query': paper.get('query', ''),
                        'ingested_at': datetime.now().isoformat()
                    }
                )
                documents.append(doc)
            
            # Dividir en chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Agregar a ChromaDB
            self._add_chunks_to_collection(chunks, source='google_scholar')
            
            logger.info(f"✅ {len(papers)} papers → {len(chunks)} chunks ingestados")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"❌ Error al ingestar papers: {e}")
            return 0
    
    def ingest_text_file(self, filepath: str, source_type: str, doc_type: str) -> int:
        """
        Ingesta archivo de texto plano
        
        Args:
            filepath: Ruta al archivo
            source_type: Tipo de fuente (becas, recursos, repositorios)
            doc_type: Tipo de documento
            
        Returns:
            Número de chunks ingestados
        """
        logger.info(f"\n📄 Ingiriendo {source_type} desde: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Crear documento
            doc = Document(
                page_content=content,
                metadata={
                    'source': source_type,
                    'type': doc_type,
                    'filename': Path(filepath).name,
                    'ingested_at': datetime.now().isoformat()
                }
            )
            
            # Dividir en chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Agregar a ChromaDB
            self._add_chunks_to_collection(chunks, source=source_type)
            
            logger.info(f"✅ {len(chunks)} chunks ingestados desde {source_type}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"❌ Error al ingestar {source_type}: {e}")
            return 0
    
    def _add_chunks_to_collection(self, chunks: List[Document], source: str):
        """
        Agrega chunks a la colección de ChromaDB
        
        Args:
            chunks: Lista de documentos chunkeados
            source: Fuente de los documentos
        """
        # Preparar datos para ChromaDB
        ids = [f"{source}_{i}_{datetime.now().timestamp()}" for i in range(len(chunks))]
        documents = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        # Agregar a la colección
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"   └─ Agregados {len(chunks)} chunks a ChromaDB")
    
    def ingest_all(self) -> Dict[str, int]:
        """
        Ingesta todos los archivos scraped
        
        Returns:
            Diccionario con conteo de chunks por fuente
        """
        logger.info("\n" + "="*80)
        logger.info("🚀 INICIANDO INGESTA DE DATOS SCRAPED A CHROMADB")
        logger.info("="*80)
        
        results = {}
        
        # 1. Papers académicos (JSON)
        papers_file = self.papers_dir / 'papers_desercion.json'
        if papers_file.exists():
            results['google_scholar'] = self.ingest_papers_json(str(papers_file))
        else:
            logger.warning(f"⚠️  No encontrado: {papers_file}")
            results['google_scholar'] = 0
        
        # 2. Repositorios ecuatorianos (TXT)
        repos_file = self.papers_dir / 'repositorios_ecuador.txt'
        if repos_file.exists():
            results['repositorios'] = self.ingest_text_file(
                str(repos_file), 
                'repositorios_ecuador', 
                'institutional_document'
            )
        else:
            logger.warning(f"⚠️  No encontrado: {repos_file}")
            results['repositorios'] = 0
        
        # 3. Políticas de becas (TXT)
        becas_file = self.papers_dir / 'politicas_becas.txt'
        if becas_file.exists():
            results['becas'] = self.ingest_text_file(
                str(becas_file), 
                'politicas_becas', 
                'scholarship_policy'
            )
        else:
            logger.warning(f"⚠️  No encontrado: {becas_file}")
            results['becas'] = 0
        
        # 4. Recursos de orientación (TXT)
        recursos_file = self.papers_dir / 'recursos_orientacion.txt'
        if recursos_file.exists():
            results['recursos'] = self.ingest_text_file(
                str(recursos_file), 
                'recursos_educativos', 
                'educational_resource'
            )
        else:
            logger.warning(f"⚠️  No encontrado: {recursos_file}")
            results['recursos'] = 0
        
        # Mostrar resumen
        self._print_ingestion_summary(results)
        
        return results
    
    def _print_ingestion_summary(self, results: Dict[str, int]):
        """Imprime resumen de la ingesta"""
        logger.info("\n" + "="*80)
        logger.info("📊 RESUMEN DE INGESTA")
        logger.info("="*80)
        
        total_chunks = sum(results.values())
        
        for source, count in results.items():
            icon = "✅" if count > 0 else "⚠️"
            logger.info(f"{icon} {source.upper()}: {count} chunks")
        
        logger.info("-" * 80)
        logger.info(f"📦 TOTAL: {total_chunks} chunks en ChromaDB")
        logger.info(f"🗂️  Colección: {self.collection_name}")
        logger.info(f"📍 Ubicación: {self.chroma_dir}")
        logger.info("="*80 + "\n")
    
    def test_rag_query(self, query: str, n_results: int = 3):
        """
        Prueba el RAG con una consulta
        
        Args:
            query: Consulta a realizar
            n_results: Número de resultados a retornar
        """
        logger.info(f"\n🔍 Probando RAG con query: '{query}'")
        logger.info("-" * 80)
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            logger.info(f"\n📚 Encontrados {len(results['documents'][0])} documentos relevantes:\n")
            
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                logger.info(f"--- Resultado {i} ---")
                logger.info(f"Fuente: {metadata.get('source', 'N/A')}")
                logger.info(f"Tipo: {metadata.get('type', 'N/A')}")
                logger.info(f"Contenido: {doc[:200]}...")
                logger.info("")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en query: {e}")
            return None
    
    def get_collection_stats(self):
        """Obtiene estadísticas de la colección"""
        count = self.collection.count()
        logger.info(f"\n📊 Estadísticas de la colección '{self.collection_name}':")
        logger.info(f"   └─ Total documentos: {count}")
        return count


def main():
    """Función principal"""
    try:
        # Inicializar ingestor
        ingestor = ScrapedDataIngestor(
            papers_dir='datos/papers_academicos',
            chroma_dir='datos/chromadb',
            collection_name='knowledge_base'
        )
        
        # Ingestar todos los datos
        results = ingestor.ingest_all()
        
        # Mostrar estadísticas
        ingestor.get_collection_stats()
        
        # Probar el RAG
        test_queries = [
            "¿Qué dice la literatura sobre factores de abandono estudiantil?",
            "¿Qué políticas de becas existen en Ecuador?",
            "¿Cuáles son las técnicas de estudio más efectivas?"
        ]
        
        logger.info("\n" + "="*80)
        logger.info("🧪 PROBANDO RAG CON CONSULTAS DE EJEMPLO")
        logger.info("="*80)
        
        for query in test_queries:
            ingestor.test_rag_query(query, n_results=2)
        
        logger.info("\n✅ Ingesta y pruebas completadas exitosamente")
        logger.info("\n🎉 El sistema RAG está listo para responder consultas!")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Error fatal: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())