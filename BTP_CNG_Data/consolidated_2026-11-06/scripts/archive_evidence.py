"""Prepare bounded authenticated draft-release ZIP assets; originals stay unchanged."""
from pathlib import Path
import argparse,csv,json,hashlib,zipfile
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
B=Path(__file__).resolve().parents[1];a.output.mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader((B/'metadata/raw_objects.csv').open()))
groups=[];current=[];size=0
for r in rows:
 if current and size+int(r['bytes'])>250*1024*1024:groups.append(current);current=[];size=0
 current.append(r);size+=int(r['bytes'])
if current:groups.append(current)
manifest=[]
for i,group in enumerate(groups,1):
 name=f'BTP_Stage3_Consolidated_2026-11-06_{i:03}.zip';dest=a.output/name
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for r in group:z.write(B/r['path'],arcname=r['path'])
 h=hashlib.sha256()
 with dest.open('rb') as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 manifest.append(dict(filename=name,bytes=dest.stat().st_size,sha256=h.hexdigest(),members=[r['path'] for r in group]))
 print(name,dest.stat().st_size,flush=True)
(B/'metadata/evidence_archive_manifest.json').write_text(json.dumps(manifest,indent=2))
