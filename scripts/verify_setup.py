"""
Verify that all core dependencies are installed correctly.
Run: python scripts/verify_setup.py
"""

def check(label, fn):
    try:
        fn()
        print(f"  ✓  {label}")
    except Exception as e:
        print(f"  ✗  {label} — {e}")

print("\n🩺 Sevam — Setup Verification\n")

check("FastAPI",             lambda: __import__("fastapi"))
check("LangChain",           lambda: __import__("langchain"))
check("OpenAI client",       lambda: __import__("openai"))
check("SentenceTransformers",lambda: __import__("sentence_transformers"))
check("FAISS",               lambda: __import__("faiss"))
check("ChromaDB",            lambda: __import__("chromadb"))
check("spaCy",               lambda: __import__("spacy"))
check("Transformers (HF)",   lambda: __import__("transformers"))
check("SQLAlchemy",          lambda: __import__("sqlalchemy"))
check("Pydantic",            lambda: __import__("pydantic"))
check("Requests",            lambda: __import__("requests"))
check("BeautifulSoup",       lambda: __import__("bs4"))
check("NumPy",               lambda: __import__("numpy"))
check("Pandas",              lambda: __import__("pandas"))

print("\nspaCy model check:")
check("en_core_web_sm", lambda: __import__("spacy").load("en_core_web_sm"))

print("\n✅ Done! If all checks pass, you're ready for Phase 1.\n")
