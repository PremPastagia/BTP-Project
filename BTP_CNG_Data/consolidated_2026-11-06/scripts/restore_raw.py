"""Restore only declared raw objects from authenticated draft release archives."""
from pathlib import Path
import argparse,csv,json,hashlib,zipfile
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args()
B=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 return h.hexdigest()
expected={r['path']:r['sha256'] for r in csv.DictReader((B/'metadata/raw_objects.csv').open())}
for receipt in json.loads((B/'metadata/evidence_archive_manifest.json').read_text()):
 archive=a.directory/receipt['filename']
 if sha(archive)!=receipt['sha256']:raise ValueError('Archive checksum mismatch: '+archive.name)
 with zipfile.ZipFile(archive) as z:
  if len(z.namelist())!=len(set(z.namelist())) or set(z.namelist())!=set(receipt['members']):raise ValueError('Archive member mismatch')
  for name in z.namelist():
   target=(B/name).resolve()
   if not target.is_relative_to(B) or name not in expected:raise ValueError('Unsafe or undeclared archive path: '+name)
   if target.exists():
    if sha(target)!=expected[name]:raise ValueError('Refusing to overwrite existing different bytes: '+name)
    continue
   target.parent.mkdir(parents=True,exist_ok=True)
   temporary=target.with_suffix(target.suffix+'.restoring')
   with z.open(name) as src,temporary.open('wb') as dst:
    import shutil;shutil.copyfileobj(src,dst)
   if sha(temporary)!=expected[name]:
    temporary.unlink();raise ValueError('Member checksum mismatch: '+name)
   temporary.replace(target)
print('RAW_RESTORED_CHECKSUMS_VERIFIED')
