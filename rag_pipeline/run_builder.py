import os, sys, json
here = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(here, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from rag_pipeline.extraction.document_builder import DocumentBuilder

inpath = os.path.join(project_root, 'rag_pipeline', 'extraction', 'repo_documents.json')
outpath = os.path.join(project_root, 'rag_pipeline', 'extraction', 'searchable_documents.json')

if not os.path.exists(inpath):
    print(f'Input file not found: {inpath}')
    sys.exit(1)

with open(inpath, 'r', encoding='utf-8') as f:
    docs = json.load(f)

# Filter code documents (have file_path key)
code_docs = [d for d in docs if isinstance(d, dict) and 'file_path' in d]
print(f'Found {len(code_docs)} code docs')

builder = DocumentBuilder()
search_docs = builder.batch_build_from_code_docs(code_docs)

with open(outpath, 'w', encoding='utf-8') as f:
    json.dump(search_docs, f, ensure_ascii=False, indent=2)

print(f'Built {len(search_docs)} searchable documents to {outpath}')
for d in search_docs[:50]:
    print(d.get('id'))
