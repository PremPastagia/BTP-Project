"""Freeze a review candidate manifest; does not imply acceptance."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1]
out=B/'metadata/snapshot_checksums.json';rows=[]
for p in sorted(B.rglob('*')):
 if not p.is_file() or p==out or '__pycache__' in p.parts or p.suffix=='.pyc':continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 rows.append(dict(path=p.relative_to(B).as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest()))
out.write_text(json.dumps(rows,indent=2))
print('REVIEW_CANDIDATE_MANIFEST_SHA256',hashlib.sha256(out.read_bytes()).hexdigest())
