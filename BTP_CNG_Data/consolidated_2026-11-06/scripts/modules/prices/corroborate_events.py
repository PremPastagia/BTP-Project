"""Reproduce bounded news receipts and manually specified source-claim checks."""
from pathlib import Path
from datetime import datetime,timezone
import requests,json,csv,re,hashlib
from bs4 import BeautifulSoup
B=Path(__file__).resolve().parent
items=[('NDTV_20230409','https://www.ndtv.com/india-news/cng-prices-in-delhi-reduced-from-today-3932389'),('NIE_20240622','https://www.newindianexpress.com/states/delhi/2024/Jun/22/cng-price-in-delhi-adjoining-cities-hiked-by-rs-1-per-kg'),('AUTOCAR_202304','https://www.autocarindia.com/industry-amp/cng-prices-slashed-by-up-to-rs-8-per-kg-second-price-cut-in-2023-427833')]
manifest_path=B/'metadata/corroboration_acquisitions.json'
receipts=json.loads(manifest_path.read_text()) if manifest_path.exists() else []
byid={r['source_id']:r for r in receipts}
for sid,url in items:
    path=B/'raw'/f'{sid}.html'
    if sid in byid and path.exists():
        assert hashlib.sha256(path.read_bytes()).hexdigest()==byid[sid]['sha256'];continue
    # Do not repeatedly retry failed/blocked sources during offline rebuild.
    if sid in byid:continue
    try:
        q=requests.get(url,timeout=35,headers={'User-Agent':'Mozilla/5.0'});q.raise_for_status();path.write_bytes(q.content)
        byid[sid]=dict(source_id=sid,url=url,final_url=q.url,local_path=str(path),sha256=hashlib.sha256(q.content).hexdigest(),retrieved_at=datetime.now(timezone.utc).isoformat(),status='downloaded',bytes=len(q.content))
    except Exception as e:byid[sid]=dict(source_id=sid,url=url,status='failed',error=str(e))
manifest_path.write_text(json.dumps(list(byid.values()),indent=2))
texts={};news=[]
for sid,r in byid.items():
    if r['status']!='downloaded':continue
    s=BeautifulSoup(Path(r['local_path']).read_bytes(),'html.parser');date_pub='';title=''
    for sc in s.find_all('script',type='application/ld+json'):
        try:
            d=json.loads(sc.string or sc.get_text());ds=d if isinstance(d,list) else [d]
            for x in ds:
                if isinstance(x,dict) and x.get('@type')=='NewsArticle':date_pub=x.get('datePublished','');title=x.get('headline','')
        except Exception:pass
    for tag in s(['script','style','nav','footer','header']):tag.decompose()
    texts[sid]=' '.join(s.stripped_strings)
    news.append(dict(source_id=sid,source_url=r['url'],source_sha256=r['sha256'],title=title,publisher_metadata_publication_timestamp=date_pub,publication_timing_status='source_timezone_disagreement_requires_review' if sid.startswith('NIE') else 'publisher_JSONLD_timestamp_not_independently_verified',event_effective_date='2024-06-22' if sid.startswith('NIE') else '',notes='NIE visible 14:09 on dated article conflicts with timezone interpretation of JSON-LD 14:09Z; do not assume exact as-of time.' if sid.startswith('NIE') else 'Article publication date is not automatically every reported effective date.'))

obs=list(csv.DictReader((B/'structured/source_price_observations.csv').open(encoding='utf-8-sig')))
checks=[]
# Original PTI reporting carried by NIE explicitly states these city prices and
# that the Saturday increase occurred on 22 June 2024. Exact claims are transcribed,
# not automatically learned from all numbers on a web page.
for geo,value in [('Delhi',75.09),('Noida',79.70),('G Noida',79.70),('Ghaziabad',79.70),('Ajmer',82.94)]:
    sid='NIE_20240622';r=byid[sid]
    assert format(value,'.2f') in texts[sid]
    hit=[x for x in obs if x['source_id']=='igl_chronology' and x['geography_name']==geo and x['effective_date']=='2024-06-22'];assert len(hit)==1
    checks.append(dict(corroborating_source_id=sid,corroborating_url=r['url'],corroborating_sha256=r['sha256'],primary_observation_id=hit[0]['observation_id'],geography_name=geo,event_effective_date='2024-06-22',source_price=value,chronology_price=hit[0]['price_inr_kg'],result='price_and_effective_date_agreement' if float(hit[0]['price_inr_kg'])==value else 'conflict',independence_limit='Independent publisher/reporting, but underlying operator announcement may be shared. Five markets in one event are not five independent events.'))
# Autocar's 10 April article reports prevailing prices, not an exact effective
# timestamp. Compare the nearby source chronology without inventing the event day.
for geo,value in [('Delhi',73.59),('Pune Municipal Corporation',87.0)]:
    sid='AUTOCAR_202304';r=byid[sid]
    assert ('73.59' if geo=='Delhi' else '87/kg') in texts[sid]
    hits=[x for x in obs if x['geography_name']==geo and (x['effective_date'].startswith('2023-04') or x['effective_window_start'].startswith('2023-04'))]
    assert len(hits)==1,(geo,len(hits))
    checks.append(dict(corroborating_source_id=sid,corroborating_url=r['url'],corroborating_sha256=r['sha256'],primary_observation_id=hits[0]['observation_id'],geography_name=geo,event_effective_date='',source_price=value,chronology_price=hits[0]['price_inr_kg'],result='price_level_agreement_effective_timing_unverified' if float(hits[0]['price_inr_kg'])==value else 'price_level_conflict_and_effective_timing_unverified',independence_limit='Article dated10 April2023 quotes prevailing level. Exact effective date not independently established; no interval-continuity claim. Disagreements retained, never corrected to make sources agree.'))
for name,rows in [('metadata/independent_price_crosschecks.csv',checks),('metadata/corroborating_news_metadata.csv',news)]:
    with (B/name).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps(dict(downloaded=sum(x['status']=='downloaded' for x in byid.values()),failed=sum(x['status']=='failed' for x in byid.values()),price_checks=len(checks),scope='Selected events only; no complete history certification'),indent=2))
