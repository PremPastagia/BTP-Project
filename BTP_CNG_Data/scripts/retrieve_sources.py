"""Stage 3 evidence retrieval. Never fills observations or claims release dates."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import csv, hashlib, json, urllib.request, urllib.parse, argparse
BASE=Path(__file__).resolve().parents[1]

def retrieve(item):
    url=urllib.parse.quote(item['url'],safe=':/?=&()%'); sid=item['source_id']; now=datetime.now(timezone.utc).isoformat()
    row=dict(item,extraction_timestamp=now)
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'BTP academic data collection; public records'})
        with urllib.request.urlopen(req,timeout=35) as r:
            data=r.read(); ctype=r.headers.get('Content-Type',''); row.update(http_status=r.status,final_url=r.url,content_type=ctype)
        digest=hashlib.sha256(data).hexdigest()
        suffix='.pdf' if data.startswith(b'%PDF') else '.xlsx' if data.startswith(b'PK') else '.xls' if data.startswith(bytes.fromhex('d0cf11e0')) else '.json' if 'json' in ctype else '.html'
        p=BASE/'raw'/'recovery'/sid/(digest+suffix);p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists(): p.write_bytes(data)
        row.update(raw_path=str(p.relative_to(BASE)),sha256=digest,bytes=len(data),status='retrieved_unparsed' if len(data) else 'empty_response',error='' if len(data) else 'HTTP success with zero bytes')
    except Exception as e: row.update(status='retrieval_failed',error=str(e),raw_path='',sha256='',bytes=0)
    return row

def main():
    a=argparse.ArgumentParser();a.add_argument('queue');args=a.parse_args()
    items=list(csv.DictReader(open(args.queue)))
    rows=list(ThreadPoolExecutor(max_workers=6).map(retrieve,items))
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    p=BASE/'logs'/('retrieval_'+stamp+'.json');p.write_text(json.dumps(rows,indent=2))
    for r in rows: print(r['source_id'],r['status'],r['bytes'],r.get('error',''))
if __name__=='__main__':main()
