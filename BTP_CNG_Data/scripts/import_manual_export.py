"""Import an authorised campus/manual export without guessing metadata or reshaping values."""
import argparse,json,shutil,hashlib
from pathlib import Path
from datetime import datetime,timezone
import pandas as pd
B=Path(__file__).resolve().parents[1]
def main():
 a=argparse.ArgumentParser();a.add_argument('file');a.add_argument('--metadata',required=True);args=a.parse_args()
 p=Path(args.file);m=json.loads(Path(args.metadata).read_text())
 for k in ['source_id','source_url','geographical_grain','units','frequency','licensing','observation_period_definition','publication_status']:
  if not m.get(k):raise ValueError('Required metadata: '+k)
 if m['publication_status']=='verified' and not(m.get('publication_release_date') and m.get('publication_evidence')):raise ValueError('Verified publication requires date and evidence.')
 if not __import__('re').fullmatch(r'[A-Za-z0-9_-]+',m['source_id']):raise ValueError('Use a stable alphanumeric source ID.')
 digest=hashlib.sha256(p.read_bytes()).hexdigest();out=B/'raw/manual'/m['source_id']/(digest+p.suffix);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
 m.update(raw_path=str(out.relative_to(B)),sha256=digest,extraction_timestamp=datetime.now(timezone.utc).isoformat(),original_filename=p.name,value_class=m.get('value_class','unverified'))
 (out.parent/(digest+'.metadata.json')).write_text(json.dumps(m,indent=2))
 tables=pd.read_excel(out,sheet_name=None) if p.suffix.lower() in ['.xls','.xlsx'] else {'source':pd.read_csv(out)} if p.suffix.lower()=='.csv' else {}
 dest=B/'structured/manual'/m['source_id'];dest.mkdir(parents=True,exist_ok=True)
 for i,(sheet,table) in enumerate(tables.items(),1):
  table.to_csv(dest/f'{digest}_sheet_{i}.csv',index=False)
  m.setdefault('tables',[]).append({'sheet':sheet,'rows':len(table),'columns':list(table.columns)})
 (dest/(digest+'.metadata.json')).write_text(json.dumps(m,indent=2));print(json.dumps(m))
if __name__=='__main__':main()
