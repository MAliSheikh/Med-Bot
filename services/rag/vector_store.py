from typing import List, Dict, Tuple
import lancedb
import os
from sentence_transformers import SentenceTransformer  # Remove later if issues

class LanceDBTextStore:
    def __init__(self, persist_directory: str = "./lancedb_db"):
        self.path = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        self.db = lancedb.connect(persist_directory)

        if "medical_docs" not in self.db.table_names():
            # Simple text + metadata schema (NO vectors!) - FIX: Added vector field
            # Further FIX: Explicitly define metadata schema to prevent 'Field not found' errors
            self.table = self.db.create_table(
                "medical_docs",
                data=[{
                    "id": "init",
                    "text": "",
                    "metadata": {
                        "source": "",
                        "page": 0,
                        "chunk_id": "",
                        "disease_name": [""], # Explicitly define as list of strings
                        "treatment_type": [""], # Explicitly define as list of strings
                        "priority": ""
                    },
                    "vector": [0.0] * 384
                }]
            )
        else:
            self.table = self.db.open_table("medical_docs")

    def add(self, ids: List[str], embeddings, metadatas: List[Dict], documents: List[str]):
        """Add medical chunks with rich metadata."""
        data = []
        for i, doc in enumerate(documents):
            data.append({
                "id": ids[i],
                "text": doc,
                "metadata": metadatas[i],
                "vector": embeddings[i]
            })
        self.table.add(data)

    def query(self, query_text: str, n_results: int = 5) -> Tuple[List[str], List[str], List[Dict]]:
        """Text search + medical metadata filtering."""
        # BM25-style text search works great for medical terms
        results = self.table.search(query_text).limit(n_results).to_pandas()
        ids = results['id'].tolist() if not results.empty else []
        texts = results['text'].tolist() if not results.empty else []
        metadatas = results['metadata'].tolist() if not results.empty else []
        return ids, texts, metadatas

def get_lancedb_collection(persist_directory: str = "./lancedb_db"):
    store = LanceDBTextStore(persist_directory)
    return store, store.table