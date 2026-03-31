import requests
import json
import numpy as np
from curriculum import get_all_lessons, STANDARDS

# ─── Embedding via Gemini API (free) ──────────────────────────
def get_embedding(text, api_key):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"text-embedding-004:embedContent?key={api_key}"
    )
    payload = {
        "model": "models/text-embedding-004",
        "content": {"parts": [{"text": text[:3000]}]}
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        data = r.json()
        return data.get("embedding", {}).get("values")
    except Exception:
        return None


def cosine_sim(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0


# ─── Build corpus chunks from curriculum ─────────────────────
def build_corpus():
    corpus = []
    for lesson in get_all_lessons():
        standards_text = " ".join(
            f"{k}: {STANDARDS.get(k,'')}" for k in lesson.get("standards", [])
        )
        vocab_text = ", ".join(lesson.get("vocabulary", []))
        full_text = "\n".join([
            f"Module: {lesson['module']}",
            f"Lesson: {lesson['name']}",
            f"Type: {lesson['type']}",
            f"Objective: {lesson['objective']}",
            f"Content:\n{lesson['key_rules']}",
            f"Vocabulary: {vocab_text}",
            f"Standards: {standards_text}",
        ])
        corpus.append({
            "lesson_id": lesson["id"],
            "lesson": lesson,
            "text": full_text,
            "vec": None,
        })
    return corpus


# ─── Embed all chunks (called once, stored in session_state) ──
def embed_corpus(corpus, api_key):
    for chunk in corpus:
        if chunk["vec"] is None:
            chunk["vec"] = get_embedding(chunk["text"], api_key)
    return corpus


# ─── Retrieve top-k relevant chunks for a query ───────────────
def retrieve(query, corpus, api_key, top_k=3):
    q_vec = get_embedding(query, api_key)
    if not q_vec:
        return []
    scored = [
        (cosine_sim(q_vec, c["vec"]), c)
        for c in corpus if c["vec"] is not None
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c["lesson"] for _, c in scored[:top_k]]


# ─── Build RAG context string from retrieved chunks ──────────
def build_context(chunks):
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}] {chunk['module']} — {chunk['name']}\n"
            f"Objective: {chunk['objective']}\n"
            f"{chunk['key_rules']}\n"
            f"Vocabulary: {', '.join(chunk.get('vocabulary', []))}"
        )
    return "\n\n---\n\n".join(parts)
