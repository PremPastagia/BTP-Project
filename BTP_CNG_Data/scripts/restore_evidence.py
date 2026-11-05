"""Restore evidence ZIPs beside their repository paths, validating each file hash."""
from pathlib import Path
import argparse,csv,hashlib,zipfile
B=Path(__file__).resolve().parents[1]
def main():
 a=argparse.ArgumentParser();a.add_argument('archives',nargs='+');args=a.parse_args()
 expected={r['path']:r for r in csv.DictReader(open(B/'metadata/evidence_file_manifest.csv'))}
 for archive in args.archives:
  with zipfile.ZipFile(archive) as z:
   for name in z.namelist():
    if name.endswith('/'):continue
    if name not in expected:raise ValueError('Unexpected member: '+name)
    p=(B/name).resolve()
    if not p.is_relative_to(B.resolve()):raise ValueError('Unsafe path')
    data=z.read(name)
    if hashlib.sha256(data).hexdigest()!=expected[name]['sha256']:raise ValueError('Checksum mismatch: '+name)
    if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()!=expected[name]['sha256']:raise ValueError('Refusing to overwrite different bytes: '+name)
    p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():p.write_bytes(data)
 print('Evidence restored; all restored member checksums match.')
if __name__=='__main__':main()
