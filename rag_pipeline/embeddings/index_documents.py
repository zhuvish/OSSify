import os, sys, json
here = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(here, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from rag_pipeline.utils.config import get_config
config = get_config()

inpath = os.path.join(project_root, 'rag_pipeline', 'extraction', 'searchable_documents.json')
if not os.path.exists(inpath):
    print('Input searchable_documents.json not found at', inpath)
    sys.exit(1)

with open(inpath, 'r', encoding='utf-8') as f:
    docs = json.load(f)

texts = [d.get('content','') for d in docs]
ids = [d.get('id') for d in docs]
metadatas = [d.get('metadata',{}) for d in docs]

print(f'Preparing to embed {len(texts)} documents using model {config.EMBEDDINGS_MODEL}')

try:
    from sentence_transformers import SentenceTransformer
except Exception as e:
    print('Failed to import sentence-transformers:', e)
    sys.exit(1)

model = SentenceTransformer(config.EMBEDDINGS_MODEL)
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

try:
    import chromadb
    from chromadb.config import Settings
except Exception as e:
    print('Failed to import chromadb:', e)
    sys.exit(1)

# Initialize client with persistent directory if configured
try:
    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=config.CHROMADB_PATH))
except Exception:
    # Fallback to default client
    client = chromadb.Client()

collection_name = getattr(config, 'CHROMADB_COLLECTION', 'ossify_documents')
try:
    collection = client.get_collection(name=collection_name)
    print('Using existing collection:', collection_name)
except Exception:
    collection = client.create_collection(name=collection_name)
    print('Created collection:', collection_name)

# Upsert documents
try:
    # chromadb expects lists; convert embeddings to list of lists
    emb_list = embeddings.tolist() if hasattr(embeddings, 'tolist') else list(embeddings)
    collection.add(ids=ids, metadatas=metadatas, documents=texts, embeddings=emb_list)
    print(f'Added {len(ids)} documents to collection {collection_name}')
except Exception as e:
    print('Failed to add documents to Chroma collection:', e)

# Persist if available
try:
    client.persist()
    print('Persisted ChromaDB')
except Exception:
    print('Client persist not available or not needed')

print('Indexing complete')
