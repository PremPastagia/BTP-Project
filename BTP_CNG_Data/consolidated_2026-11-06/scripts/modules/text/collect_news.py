"""Recover saved public article evidence and retain publisher date claims; no NLP features."""
from pathlib import Path
import csv, json, hashlib, datetime, concurrent.futures, re, html
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import requests
from bs4 import BeautifulSoup

ROOT=Path('/Users/virajvekariya/Desktop/[ME] BTP')
BASE=Path(__file__).parent
FRESH=ROOT/'BTP/BTP_CNG_Fresh_2026-11-06/text'
PR=ROOT/'Stage3_GitHub_Audit_2026-11-06/snapshots/github-pr1/BTP_CNG_Data'
for name in ['raw','structured','metadata']: (BASE/name).mkdir(exist_ok=True,parents=True)
def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(url):
 p=urlsplit(url);return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path,urlencode([(k,v) for k,v in parse_qsl(p.query) if k not in ['from','utm_source','utm_medium','utm_campaign']]),''))
def read(path):return list(csv.DictReader(path.open(encoding='utf-8-sig')))
local={}
for r in json.loads((ROOT/'Stage3_GitHub_Audit_2026-11-06/local_inventory.json').read_text()):local.setdefault(r['sha256'],ROOT/r['path'])
items=[]
for r in read(FRESH/'structured/news_archive_metadata.csv'):
 items.append(dict(url=r['url'],expected_sha256=r['sha256'],original_publication_claim=r['publication_date'],title_claim=r['title'],origin='fresh',source_id=r['source_id']))
for r in read(PR/'structured/news/actual_article_metadata.csv'):
 items.append(dict(url=r['source_url'],expected_sha256=r['raw_sha256'],original_publication_claim=r['publication_release_date'],title_claim=r['title'],origin='github-pr1',source_id=r['source_id']))
def date_claims(soup):
 dates=[]
 def walk(x):
  if isinstance(x,dict):
   types=x.get('@type',[]); types=[types] if isinstance(types,str) else types
   if any(t in ['NewsArticle','Article','ReportageNewsArticle','BlogPosting'] for t in types) and x.get('datePublished'):
    dates.append(('JSON-LD datePublished',str(x['datePublished'])))
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 for s in soup.find_all('script',type='application/ld+json'):
  try:walk(json.loads(s.string or s.get_text()))
  except (ValueError,TypeError):pass
 for tag in soup.find_all('meta'):
  key=(tag.get('property') or tag.get('name') or '').lower()
  if key in ['article:published_time','datepublished','pubdate','publishdate','og:published_time'] and tag.get('content'):dates.append((key,tag['content']))
 return list(dict.fromkeys(dates))
def fetch(item):
 r=dict(item);expected=r['expected_sha256'];p=local.get(expected);retrieved_at='';method='reused_existing_exact_hash'
 if p and p.is_file() and sha(p.read_bytes())==expected:data=p.read_bytes()
 else:
  cache=BASE/'metadata'/('url_'+sha(r['url'].encode())+'.json')
  if cache.exists():
   prior=json.loads(cache.read_text());p=Path(prior.get('source_path',''))
   if p.is_file() and prior.get('retrieved_sha256')==sha(p.read_bytes()):return prior
  try:
   resp=requests.get(r['url'],headers={'User-Agent':'Mozilla/5.0 (compatible; BTPResearch/1.0)','Accept':'text/html'},timeout=(10,30))
   r['http_status']=resp.status_code;r['final_url']=resp.url;resp.raise_for_status();data=resp.content
   retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat();h=sha(data);p=BASE/'raw'/(h+'.html');p.write_bytes(data);method='direct_original_url'
  except Exception as e:
   r.update(status='retrieval_failed',error=str(e));return r
 soup=BeautifulSoup(data,'html.parser');title=soup.title.get_text(' ',strip=True) if soup.title else ''
 bad=any(x in title.lower() for x in ['just a moment','access denied','403 forbidden','error 404'])
 claims=date_claims(soup);pub=claims[0][1] if claims else ''
 if not pub and r['origin']=='fresh' and r['url'].endswith('PressRelease09032024.html'):
  txt=soup.get_text(' ',strip=True)
  if re.search(r'\b(?:09|9)[./-]0?3[./-]2024\b',txt):pub='2024-03-09';claims=[('explicit official press-release heading','2024-03-09')]
 r.update(source_path=str(p),retrieved_sha256=sha(data),matches_previous_hash=sha(data)==expected,retrieved_at=retrieved_at,retrieval_method=method,title=title,publication_date=pub,publication_date_claims=claims,date_status='publisher_date_claim_preserved' if pub else 'unknown',status='excluded_nonarticle_response' if bad else 'retained_public_html',historical_availability_status='publisher_claim_not_independent_archive_verification',redistribution_license='not_established_no_public_full_text_release',synthetic=False)
 if pub and r['original_publication_claim'] and pub!=r['original_publication_claim']:r['date_disagreement']='current_metadata_differs_from_prior_claim_requires_review'
 (BASE/'metadata'/('url_'+sha(r['url'].encode())+'.json')).write_text(json.dumps(r,indent=2))
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:receipts=list(pool.map(fetch,items))
(BASE/'metadata/acquisition_receipts.json').write_text(json.dumps(receipts,indent=2))
seen={};rows=[];aliases=[];date_reviews=[]
def normalize_date(value):
 value=html.unescape(value).strip()
 try:
  if re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
   datetime.date.fromisoformat(value);return value,'date_only_time_unknown'
  dt=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
  return dt.isoformat(),'timestamp_with_timezone' if dt.tzinfo else 'timestamp_timezone_unknown'
 except ValueError:return '','invalid_publication_claim'
for r in receipts:
 if r.get('status')!='retained_public_html':continue
 key=(canonical(r['url']),r['retrieved_sha256']);rid=sha(json.dumps(key).encode())[:24]
 if key in seen:aliases.append(dict(article_id=rid,source_id=r['source_id'],origin=r['origin']));continue
 seen[key]=rid
 normalized=[(basis,*normalize_date(v),v) for basis,v in r['publication_date_claims']]
 # Compare instants without silently interpreting date-only precision as midnight.
 def instant(value):
  dt=datetime.datetime.fromisoformat(value)
  return dt.astimezone(datetime.timezone.utc).isoformat() if dt.tzinfo else value
 distinct={instant(v) for _,v,_,_ in normalized if v}
 pub,precision=normalize_date(r['publication_date'])
 if len(distinct)>1:
  date_reviews.append(dict(article_id=rid,claims=normalized,issue='multiple_publication_claims_require_review'))
  pub='';precision='conflicting_publisher_date_claims'
 rows.append(dict(article_id=rid,source_url=r['url'],publisher=urlsplit(r['url']).netloc,title=r.get('title') or r['title_claim'],publication_date=pub,publication_date_raw=r['publication_date'],publication_date_precision=precision,publication_date_basis=json.dumps(r['publication_date_claims']),event_date='',source_path=r['source_path'],sha256=r['retrieved_sha256'],source_version_matches_prior=r['matches_previous_hash'],publication_verification_status=r['historical_availability_status'],license_status=r['redistribution_license'],syndication_group='',synthetic=False))
with (BASE/'structured/news_metadata.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['article_id']);w.writeheader();w.writerows(rows)
checks=[{'article_id':r['article_id'],'hash_matches':sha(Path(r['source_path']).read_bytes())==r['sha256']} for r in rows]
assert all(r['hash_matches'] for r in checks)
summary=dict(receipts=len(receipts),retained_articles=len(rows),dated_articles=sum(bool(r['publication_date']) for r in rows),failed_or_excluded=[r for r in receipts if r.get('status')!='retained_public_html'],hash_checks=checks,aliases=aliases,stage3_complete=False,limitations=['Seed sample is not a representative historical news corpus','Publication metadata is a publisher claim, not independently proven original release time','Syndication and semantic duplication remain unclassified','No sentiment, collocations, event-volume features or modeling performed'])
(BASE/'metadata/validation.json').write_text(json.dumps(summary,indent=2))
(BASE/'metadata/date_claim_review.json').write_text(json.dumps(date_reviews,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k not in ['hash_checks','failed_or_excluded']},indent=2))
