"""
Vector Database for Image Embeddings
Using ChromaDB for efficient similarity search
"""

import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Optional
import uuid
from pathlib import Path
import shutil
import logging


class VectorStore:
    """
    Vector database for storing and searching image embeddings
    
    ChromaDB is a free, lightweight vector database perfect for MVP.
    Alternatives: Milvus (more complex), Pinecone (limited free tier)
    """
    
    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "image_embeddings"
    ):
        """
        Initialize ChromaDB vector store
        
        Args:
            persist_directory: Directory to persist database
            collection_name: Name of the collection
        """
        self.logger = logging.getLogger(__name__)
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.client = None
        self.collection = None

        self._initialize_collection(collection_name)
        
        print(f"✓ Vector store initialized")
        print(f"  Collection: {collection_name}")
        print(f"  Items: {self.collection.count()}")

    def _initialize_collection(self, collection_name: str) -> None:
        """
        Initialize client and collection with graceful recovery if the persisted
        database is incompatible with the current Chroma version.
        """
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Image embeddings for visual search"}
            )
        except Exception as exc:
            message = str(exc).lower()
            if "no such column" in message or "operationalerror" in message:
                self.logger.warning(
                    "Chroma persistence at %s is incompatible with the current version. "
                    "Resetting the vector store.",
                    self.persist_directory
                )
                if self.client is not None:
                    try:
                        self.client.reset()
                    except Exception:
                        pass
                    finally:
                        self.client = None
                        self.collection = None

                # Remove persisted files safely
                if self.persist_directory.exists():
                    shutil.rmtree(self.persist_directory, ignore_errors=True)
                self.persist_directory.mkdir(parents=True, exist_ok=True)

                self.client = chromadb.PersistentClient(
                    path=str(self.persist_directory),
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                self.collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"description": "Image embeddings for visual search"}
                )
            else:
                raise
    
    def add(
        self,
        embeddings: List[np.ndarray],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict]] = None
    ) -> List[str]:
        """
        Add embeddings to the database
        
        Args:
            embeddings: List of embedding vectors
            ids: Optional list of IDs (auto-generated if not provided)
            metadatas: Optional list of metadata dicts
            
        Returns:
            List of IDs for added embeddings
        """
        # Convert numpy arrays to lists
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in embeddings]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings_list,
            ids=ids,
            metadatas=metadatas
        )
        
        return ids
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar embeddings
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of results with id, similarity, and metadata
        """
        # Convert to list
        query_list = query_embedding.tolist()
        
        # Prepare where clause for filtering
        where = filter_metadata if filter_metadata else None
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_list],
            n_results=top_k,
            where=where
        )
        
        # Format results
        formatted_results = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get(self, ids: List[str]) -> List[Dict]:
        """
        Get embeddings by IDs
        
        Args:
            ids: List of IDs to retrieve
            
        Returns:
            List of items with embeddings and metadata
        """
        results = self.collection.get(ids=ids, include=['embeddings', 'metadatas'])
        
        items = []
        for i, id in enumerate(results['ids']):
            items.append({
                'id': id,
                'embedding': np.array(results['embeddings'][i]),
                'metadata': results['metadatas'][i] if results['metadatas'] else {}
            })
        
        return items
    
    def delete(self, ids: List[str]) -> None:
        """
        Delete embeddings by IDs
        
        Args:
            ids: List of IDs to delete
        """
        self.collection.delete(ids=ids)
    
    def update(
        self,
        ids: List[str],
        embeddings: Optional[List[np.ndarray]] = None,
        metadatas: Optional[List[Dict]] = None
    ) -> None:
        """
        Update embeddings and/or metadata
        
        Args:
            ids: List of IDs to update
            embeddings: Optional new embeddings
            metadatas: Optional new metadata
        """
        update_kwargs = {'ids': ids}
        
        if embeddings:
            update_kwargs['embeddings'] = [emb.tolist() for emb in embeddings]
        
        if metadatas:
            update_kwargs['metadatas'] = metadatas
        
        self.collection.update(**update_kwargs)
    
    def clear(self) -> None:
        """Clear all items from the collection"""
        # Delete collection and recreate
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"description": "Image embeddings for visual search"}
        )
        print("✓ Collection cleared")
    
    def get_stats(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dict with count and other stats
        """
        count = self.collection.count()
        
        return {
            'total_items': count,
            'collection_name': self.collection.name,
            'persist_directory': str(self.persist_directory)
        }
    
    def export_to_numpy(self, output_path: str) -> None:
        """
        Export all embeddings to numpy file for backup/migration
        
        Args:
            output_path: Path to save .npz file
        """
        # Get all items
        all_data = self.collection.get(include=['embeddings', 'metadatas'])
        
        # Save to numpy
        np.savez(
            output_path,
            ids=all_data['ids'],
            embeddings=np.array(all_data['embeddings']),
            metadatas=all_data['metadatas']
        )
        
        print(f"✓ Exported {len(all_data['ids'])} embeddings to {output_path}")
    
    def import_from_numpy(self, input_path: str) -> None:
        """
        Import embeddings from numpy file
        
        Args:
            input_path: Path to .npz file
        """
        # Load from numpy
        data = np.load(input_path, allow_pickle=True)
        
        # Add to collection
        self.add(
            embeddings=data['embeddings'],
            ids=data['ids'].tolist(),
            metadatas=data['metadatas'].tolist()
        )
        
        print(f"✓ Imported {len(data['ids'])} embeddings from {input_path}")


# Example usage
if __name__ == "__main__":
    # Initialize vector store
    store = VectorStore()
    
    # Create sample embeddings (512-dimensional)
    print("\nAdding sample embeddings...")
    
    num_samples = 10
    embedding_dim = 512
    
    sample_embeddings = [
        np.random.randn(embedding_dim).astype(np.float32)
        for _ in range(num_samples)
    ]
    
    # Normalize embeddings
    sample_embeddings = [
        emb / np.linalg.norm(emb) for emb in sample_embeddings
    ]
    
    # Create metadata
    metadatas = [
        {
            'object': f'object_{i}',
            'source': 'test',
            'category': 'furniture' if i % 2 == 0 else 'electronics'
        }
        for i in range(num_samples)
    ]
    
    # Add to database
    ids = store.add(
        embeddings=sample_embeddings,
        metadatas=metadatas
    )
    
    print(f"Added {len(ids)} embeddings")
    
    # Search
    print("\nSearching for similar items...")
    query_embedding = sample_embeddings[0]  # Use first item as query
    
    results = store.search(query_embedding, top_k=3)
    
    print(f"Found {len(results)} results:")
    for result in results:
        print(f"  ID: {result['id'][:8]}... | Similarity: {result['similarity']:.3f} | {result['metadata']}")
    
    # Filter search
    print("\nFiltered search (furniture only)...")
    results = store.search(
        query_embedding,
        top_k=3,
        filter_metadata={'category': 'furniture'}
    )
    
    print(f"Found {len(results)} furniture items")
    
    # Stats
    print("\nDatabase stats:")
    stats = store.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

