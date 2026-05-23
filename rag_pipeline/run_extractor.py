import sys, os, json
# Ensure project root is on sys.path
here = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(here, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from rag_pipeline.extraction.code_extractor import CodeExtractor

if len(sys.argv) < 2:
    print('Usage: python run_extractor.py <repo_path>')
    sys.exit(2)
repo_path = sys.argv[1]
ce = CodeExtractor(repo_path)
docs = ce.extract_files()
outpath = os.path.join(project_root, 'rag_pipeline', 'extraction', 'repo_documents.json')
with open(outpath, 'w', encoding='utf-8') as f:
    json.dump(docs, f, ensure_ascii=False, indent=2)
print(f'Extracted {len(docs)} files to {outpath}')
for d in docs[:50]:
    print(d.get('file_path'))
