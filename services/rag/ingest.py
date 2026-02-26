import os, sys, uuid, gc
from pypdf import PdfReader
import hashlib, re, math
import shutil

from services.rag.vector_store import get_lancedb_collection

def _simple_embed(text: str):
    """Create a simple embedding using word hash vectors."""
    dim = 384
    words = re.findall(r'\w+', text.lower())
    embedding = [0.0] * dim
    for word in words:
        hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
        idx = hash_val % dim
        embedding[idx] += 1.0
    # Normalize
    norm = math.sqrt(sum(x**2 for x in embedding))
    if norm > 0:
        embedding = [x / norm for x in embedding]
    return embedding

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

# 🔥 NEW: Medical content filter
def is_medical_content(text):
    """Filter ONLY medical/clinical content - Skip management theory"""
    text_lower = text.lower()
    medical_keywords = [
        'fever', 'temperature', 'pain', 'dosage', 'mg', 'tablet', 'injection',
        'treatment', 'symptom', 'diagnosis', 'patient', 'medicine', 'protocol',
        'antibiotics', 'insulin', 'paracetamol', 'ibuprofen', 'aspirin',
        'hypertension', 'diabetes', 'pneumonia', 'asthma', 'infection'
    ]
    management_keywords = [
        'management', 'organization', 'healthcare system', 'nhs', 'policy',
        'reform', 'managerial', 'capacity', 'institutional', 'governance'
    ]
    
    # Must have medical keywords AND NOT management theory
    has_medical = any(kw in text_lower for kw in medical_keywords)
    is_management = any(kw in text_lower for kw in management_keywords)
    
    return has_medical and not is_management

def extract_medical_metadata(text, source_file, page_num, chunk_id):
    text_lower = text.lower()
    diseases = ["diabetes", "hypertension", "pneumonia", "fever", "asthma"]
    treatments = ["antibiotics", "insulin", "paracetamol", "surgery", "ibuprofen"]
    return {
        "source": os.path.basename(source_file), "page": page_num,
        "chunk_id": chunk_id, 
        "disease_name": [d.title() for d in diseases if d in text_lower],
        "treatment_type": [t.title() for t in treatments if t in text_lower],
        "priority": "high" if any(word in text_lower for word in ["emergency", "urgent", "fever"]) else "normal"
    }

def add_chunks_fast(store, collection, ids, embeddings, metadatas, documents):
    data = [{"id": ids[i], "vector": embeddings[i], "text": documents[i][:800], "metadata": metadatas[i]}
            for i in range(len(ids))]
    collection.add(data)

def index_pdfs(pdf_paths, persist_directory="./lancedb_db"):
    # Clear database for fresh medical-only indexing
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print(f"🗑️ Cleared LanceDB: {persist_directory}")
    
    store, collection = get_lancedb_collection(persist_directory)
    all_ids, all_embeds, all_meta, all_docs = [], [], [], []
    medical_chunks = 0

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        fname = os.path.basename(pdf_path)
        print(f"📄 Processing: {fname}")

        for page_num, page in enumerate(reader.pages):  # Check all pages
        # for page_num, page in enumerate(reader.pages[:30]):  # Check all 30 pages
            text = page.extract_text()
            if len(text) < 200: continue
            
            chunks = chunk_text_safe(text)
            if not chunks: continue
            
            embeds = [_simple_embed(c) for c in chunks]
            
            for i, chunk in enumerate(chunks):
                # 🔥 MEDICAL FILTER - Only clinical content!
                if is_medical_content(chunk):
                    cid = f"{fname}_p{page_num}_c{i}"
                    meta = extract_medical_metadata(chunk, pdf_path, page_num+1, i)
                    all_ids.append(cid)
                    all_embeds.append(embeds[i])
                    all_meta.append(meta)
                    all_docs.append(chunk)
                    medical_chunks += 1
                    print(f"✅ Medical chunk {medical_chunks}: {fname} p{page_num+1}")

    print(f"📊 MEDICAL CHUNKS INDEXED: {medical_chunks}")
    
    if all_ids:
        print("💾 Saving to LanceDB...")
        add_chunks_fast(store, collection, all_ids, all_embeds, all_meta, all_docs)
        print(f"✅ SUCCESS: {medical_chunks} MEDICAL chunks indexed!")
    else:
        print("❌ NO MEDICAL CONTENT FOUND - Check your PDFs!")

if __name__ == "__main__":
    pdfs = ["/content/clinical_medicine_ashok_chandra.pdf", '/content/Food borne diseases.pdf', '/content/Managing modern healthcare.pdf']
    
    index_pdfs(pdfs)
