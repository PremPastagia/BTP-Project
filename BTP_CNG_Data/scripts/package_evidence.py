"""Package large immutable source evidence outside git, preserving repository paths."""
from pathlib import Path
import csv,json,zipfile,hashlib
from recover_repository import B,sha
OUT=B.parents[1]/'BTP_Stage3_Evidence';OUT.mkdir(exist_ok=True)
def main():
 files=sorted(p for folder in ['raw/recovery','documents/extracted','documents/ocr'] for p in (B/folder).rglob('*') if p.is_file())
 batches=[];batch=[];size=0
 for p in files:
  n=p.stat().st_size
  if batch and size+n>200*1024*1024:batches.append(batch);batch=[];size=0
  batch.append(p);size+=n
 if batch:batches.append(batch)
 manifest=[];packs=[]
 for i,batch in enumerate(batches,1):
  dest=OUT/f'BTP_Stage3_Evidence_{i:02d}.zip'
  with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
   for p in batch:
    rel=str(p.relative_to(B));z.write(p,rel);manifest.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha(p),bundle=dest.name))
  packs.append(dict(filename=dest.name,local_path=str(dest),bytes=dest.stat().st_size,sha256=sha(dest),file_count=len(batch)))
  print(dest.name,dest.stat().st_size,len(batch),flush=True)
 with open(B/'metadata/evidence_file_manifest.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=manifest[0]);w.writeheader();w.writerows(manifest)
 with open(B/'metadata/evidence_bundles.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=packs[0]);w.writeheader();w.writerows(packs)
 (OUT/'upload_request.json').write_text(json.dumps({'uploads':[{'local_path':p['local_path'],'purpose':'create_library_file','library_artifact_type':'other'} for p in packs]}))
 print(len(files),'files in',len(packs),'bundles')
if __name__=='__main__':main()
