import os
import sys
from openai import OpenAI
import hashlib
import re
import math
from core.config import GROQ_API_KEY, GROQ_API_URL, HUGGING_FACE_API_KEY, HUGGING_FACE_API_URL
from services.rag.vector_store import get_lancedb_collection
from services.report.prompt import get_rag_chat_guardrail_prompt

# GROQ_API_KEY = GROQ_API_KEY
# GROQ_API_URL = GROQ_API_URL
print("GROQ_API_KEY:", GROQ_API_KEY)
print("GROQ_API_URL:", GROQ_API_URL)
print("HUGGING_FACE_API_KEY:", HUGGING_FACE_API_KEY)
print("HUGGING_FACE_API_URL:", HUGGING_FACE_API_URL)
GROQ_CHAT_MODEL = "openai/gpt-oss-120b"
GROQ_EMBED_MODEL = "nomic-embed-text"

# Simple embedding function using word hashing (no API needed)
def _simple_embed(text: str, dim: int = 384) -> list:
    """Create a simple embedding using word hash vectors."""
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



def retrieve_docs(collection, query_embedding, top_k=5, metadata_filter: dict = None):
    """Retrieve documents from a LanceTable object using vector search."""
    # LanceDB uses .search() for vector similarity search, which returns a builder.
    # We then limit the results and convert to a list of dictionaries.
    results = collection.search(query_embedding).limit(top_k).to_list()

    ids = [r['id'] for r in results]
    texts = [r['text'] for r in results]
    metadatas = [r['metadata'] for r in results]
    return ids, texts, metadatas


def embed_query(text: str):
    """Embed query using simple built-in hash-based embedding."""
    return _simple_embed(text)


def answer_query(user_question: str, user_info: dict = None, past_reports: list = None, top_k=5):
    """Run a RAG query.

    The `user_question` is embedded for retrieval and also forwarded to the
    guardrail prompt so the model knows what to answer.
    """

    # 1) embed query
    print("DEBUG: Embedding query...")
    q_emb = embed_query(user_question)

    # 2) retrieve top docs
    print("DEBUG: Retrieving docs from LanceDB...")
    store, collection = get_lancedb_collection()
    ids, docs, metadatas = retrieve_docs(collection, q_emb, top_k=top_k)
    print(f"DEBUG: Retrieved {len(docs)} docs.")

    # 3) build context
    context_text = "\n\n---\n\n".join([f"[source={m.get('source')} page={m.get('page')}]\n{d}" for m,d in zip(metadatas, docs)])

    # 4) build prompt using guardrail prompt and include the question
    prompt = get_rag_chat_guardrail_prompt(
        context_text,
        user_info=user_info,
        past_reports=past_reports,
        question=user_question,
    )

    # 5) call chat completion via Groq (using OpenAI-compatible API)
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set")

    print(f"DEBUG: Sending request to Groq ({GROQ_CHAT_MODEL})...")
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    chat_resp = client.chat.completions.create(
        model=GROQ_CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.0,
    )
    print("DEBUG: Response received.")
    return chat_resp
