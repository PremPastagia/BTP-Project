"""OCR scan-only PPAC notifications. Output is explicitly unverified transcription."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,tempfile,json
from recover_repository import B

def one(p):
 out=B/'documents/ocr'/p.parent.name/(p.stem+'.txt');out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():return {'source_id':p.parent.name,'status':'cached_ocr','text_path':str(out.relative_to(B))}
 try:
  with tempfile.TemporaryDirectory() as td:
   stem=Path(td)/'page';subprocess.run(['pdftoppm','-f','1','-singlefile','-r','180','-png',str(p),str(stem)],check=True,capture_output=True,timeout=60)
   r=subprocess.run(['tesseract',str(stem)+'.png','stdout','-l','eng'],check=True,capture_output=True,timeout=60);out.write_bytes(r.stdout)
  return {'source_id':p.parent.name,'status':'ocr_unverified','text_path':str(out.relative_to(B))}
 except Exception as e:return {'source_id':p.parent.name,'status':'ocr_failed','error':str(e)}
def main():
 files=[]
 for p in (B/'raw/recovery').glob('PPAC_NOTE_*/*.pdf'):
  native=B/'documents/extracted'/p.parent.name/(p.stem+'.txt')
  if native.exists() and len(native.read_text().strip())<150:files.append(p)
 rows=list(ThreadPoolExecutor(max_workers=4).map(one,files));(B/'logs/ocr_notifications.json').write_text(json.dumps(rows,indent=2));print(len(rows),'scan-only notifications processed')
if __name__=='__main__':main()
