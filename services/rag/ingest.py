import os, sys, uuid, gc
from pypdf import PdfReader
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.config import GROQ_API_KEY
from services.rag.vector_store import get_lancedb_collection
import hashlib, re, math
import shutil # Import shutil for directory removal

def _simple_embed(text: str):
    words = re.findall(r'\w+', text.lower())[:10]
    embedding = [0.0] * 384
    for word in words:
        idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % 384
        embedding[idx] += 1
    norm = math.sqrt(sum(x**2 for x in embedding))
    return [x/norm if norm else 0 for x in embedding]

def chunk_text_safe(text):
    sentences = re.split(r'[.!?]+', text)
    chunks, current = [], ""
    for s in sentences:
        s = s.strip()
        if len(s) < 15: continue
        if len(current + s) > 1000:
            if len(current) > 150: chunks.append(current)
            current = s + ". "
        else: current += s + ". "
    if len(current) > 150: chunks.append(current)
    return chunks[:8]

def extract_medical_metadata(text, source_file, page_num, chunk_id):
    text_lower = text.lower()
    diseases = ["diabetes", "hypertension", "pneumonia"]
    treatments = ["antibiotics", "insulin", "surgery"]
    return {
        "source": os.path.basename(source_file), "page": page_num,
        "chunk_id": chunk_id, "disease_name": [d.title() for d in diseases if d in text_lower],
        "treatment_type": [t.title() for t in treatments if t in text_lower],
        "priority": "high" if "emergency" in text_lower else "normal"
    }

def add_chunks_fast(store, collection, ids, embeddings, metadatas, documents):
    data = [{"id": ids[i], "vector": embeddings[i], "text": documents[i][:800], "metadata": metadatas[i]}
            for i in range(len(ids))]
    collection.add(data)

def index_pdfs(pdf_paths, persist_directory="./lancedb_db"):
    # Remove the existing database directory to force recreation with the correct schema
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print(f"🗑️ Removed existing LanceDB directory: {persist_directory}")

    store, collection = get_lancedb_collection(persist_directory)
    all_ids, all_embeds, all_meta, all_docs = [], [], [], []

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        fname = os.path.basename(pdf_path)

        for page_num, page in enumerate(reader.pages[:15]):  # Only first 15 pages
            text = page.extract_text()
            if len(text) < 200: continue

            chunks = chunk_text_safe(text)
            if not chunks: continue

            embeds = [_simple_embed(c) for c in chunks]

            for i, chunk in enumerate(chunks):
                cid = f"{fname}_p{page_num}_c{i}"
                meta = extract_medical_metadata(chunk, pdf_path, page_num+1, i)
                all_ids.append(cid)
                all_embeds.append(embeds[i])
                all_meta.append(meta)
                all_docs.append(chunk)

    if all_ids:
        add_chunks_fast(store, collection, all_ids, all_embeds, all_meta, all_docs)

if __name__ == "__main__":
    pdfs = ["medical_rag_detailed_30_diseases.pdf"]
    index_pdfs(pdfs)
    print(f"✅ Done! {len(pdfs)} PDFs indexed")