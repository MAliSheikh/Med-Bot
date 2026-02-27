from typing import List, Dict, Tuple
import lancedb
import os
import shutil
import signal

# Check for signal support (not available on Windows)
HAS_ALARM = hasattr(signal, 'SIGALRM') and hasattr(signal, 'alarm')

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("LanceDB connection timeout")

class LanceDBTextStore:
    def __init__(self, persist_directory: str = "./lancedb_db"):
        self.path = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # If database seems corrupted (process hangs), remove and recreate
        try:
            print(f"DEBUG: Connecting to LanceDB at {persist_directory}...")
            
            # Set a timeout to detect hangs
            if HAS_ALARM:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(5)  # 5 second timeout
            
            self.db = lancedb.connect(persist_directory)
            
            if HAS_ALARM:
                signal.alarm(0)  # Cancel alarm
            print("DEBUG: LanceDB connected successfully")
        except (TimeoutException, Exception) as e:
            if HAS_ALARM:
                signal.alarm(0)  # Cancel alarm
            print(f"DEBUG: LanceDB connection failed or timed out: {e}")
            print(f"DEBUG: Removing corrupted database at {persist_directory}")
            
            # Remove corrupted database
            if os.path.exists(persist_directory):
                shutil.rmtree(persist_directory)
            
            os.makedirs(persist_directory, exist_ok=True)
            print(f"DEBUG: Reconnecting to fresh database...")
            self.db = lancedb.connect(persist_directory)

        print("DEBUG: Checking for medical_docs table...")
        try:
            if HAS_ALARM:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(5)  # 5 second timeout
            
            table_names = self.db.table_names()
            
            if HAS_ALARM:
                signal.alarm(0)
            print(f"DEBUG: Available tables: {table_names}")
        except (TimeoutException, Exception) as e:
            if HAS_ALARM:
                signal.alarm(0)
            print(f"DEBUG: Error getting table names: {e}")
            table_names = []
        
        if "medical_docs" not in table_names:
            print("DEBUG: Creating medical_docs table...")
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
            print("DEBUG: medical_docs table created successfully")
        else:
            print("DEBUG: Opening existing medical_docs table...")
            try:
                if HAS_ALARM:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(5)
                self.table = self.db.open_table("medical_docs")
                if HAS_ALARM:
                    signal.alarm(0)
                print("DEBUG: medical_docs table opened successfully")
            except (TimeoutException, Exception) as e:
                if HAS_ALARM:
                    signal.alarm(0)
                print(f"DEBUG: Error opening table: {e}. Recreating...")
                # Recreate the table
                self.table = self.db.create_table(
                    "medical_docs",
                    data=[{
                        "id": "init",
                        "text": "",
                        "metadata": {
                            "source": "",
                            "page": 0,
                            "chunk_id": "",
                            "disease_name": [""],
                            "treatment_type": [""],
                            "priority": ""
                        },
                        "vector": [0.0] * 384
                    }]
                )

    def add(self, ids: List[str], embeddings, metadatas: List[Dict], documents: List[str]):
        """Add medical chunks with rich metadata."""
        try:
            if HAS_ALARM:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(10)  # 10 second timeout for adding data
            
            data = []
            for i, doc in enumerate(documents):
                data.append({
                    "id": ids[i],
                    "text": doc,
                    "metadata": metadatas[i],
                    "vector": embeddings[i]
                })
            self.table.add(data)
            if HAS_ALARM:
                signal.alarm(0)
        except (TimeoutException, Exception) as e:
            if HAS_ALARM:
                signal.alarm(0)
            print(f"ERROR in add: {e}")
            raise

    def query(self, query_text: str, n_results: int = 5) -> Tuple[List[str], List[str], List[Dict]]:
        """Text search + medical metadata filtering."""
        try:
            if HAS_ALARM:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(10)  # 10 second timeout for querying
            
            # BM25-style text search works great for medical terms
            results = self.table.search(query_text).limit(n_results).to_list()
            
            if HAS_ALARM:
                signal.alarm(0)
            
            ids = [r['id'] for r in results]
            texts = [r['text'] for r in results]
            metadatas = [r['metadata'] for r in results]
            return ids, texts, metadatas
        except (TimeoutException, Exception) as e:
            if HAS_ALARM:
                signal.alarm(0)
            print(f"ERROR in query: {e}")
            raise

def get_lancedb_collection(persist_directory: str = "./lancedb_db"):
    store = LanceDBTextStore(persist_directory)
    return store, store.table