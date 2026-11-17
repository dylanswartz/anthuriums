#!/usr/bin/env python3
"""Stage factual name candidates separately from trusted taxonomy/cross research."""
import argparse,datetime,hashlib,ipaddress,json,math,os,re,tempfile,time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.error import HTTPError
from urllib.robotparser import RobotFileParser
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.refresh_wcvp import fetch
ROOT=Path(__file__).resolve().parents[1]
AGENT='AnthuriumAtlasResearch'

def public_https(url):
 parts=urlsplit(url)
 if parts.scheme!='https' or not parts.hostname or parts.username or parts.password or parts.port not in (None,443):raise ValueError('Use public HTTPS source URLs without credentials or custom ports')
 host=parts.hostname.lower()
 if host=='localhost' or '.' not in host or host.endswith(('.local','.internal','.localhost')):raise ValueError('Local source hosts are not allowed')
 try:ip=ipaddress.ip_address(host)
 except ValueError:pass
 else:
  if not ip.is_global:raise ValueError('Non-public IP source is not allowed')
 return parts

# Verified site terms forbid automation even if an owner mistakenly allowlists it.
AUTOMATION_PROHIBITED={'granthuriums.com','nsetropicals.com','carnivero.com'}
def automated_source_allowed(url):
 host=public_https(url).hostname.lower().rstrip('.')
 if any(host==blocked or host.endswith('.'+blocked) for blocked in AUTOMATION_PROHIBITED):
  raise ValueError('Automated discovery prohibited by reviewed source terms; use manual citation/local import only')

def interval_seconds(value):
 if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<1:
  raise ValueError('Minimum request interval must be a finite number of at least 1 second')
 return float(value)

class RequestGate:
 """Conservatively space all requests to an origin, including robots.txt."""
 def __init__(self):self.last={}
 def fetch(self,url,limit,interval):
  origin=urlsplit(url).netloc.lower()
  while origin in self.last:
   remaining=interval-(time.monotonic()-self.last[origin])
   if remaining<=0:break
   time.sleep(min(remaining,30))
  try:return fetch(url,limit)
  finally:self.last[origin]=time.monotonic()

def robots_policy(url,gate,minimum):
 parts=public_https(url);robots=parts.scheme+'://'+parts.netloc+'/robots.txt'
 try:policy=gate.fetch(robots,1000000,minimum).decode('utf-8')
 except HTTPError as error:
  if error.code in (404,410):return {'note':'No published robots policy: HTTP '+str(error.code),'parser':None,'interval':minimum}
  raise
 parser=RobotFileParser();parser.parse(policy.splitlines())
 interval=minimum
 # Conservatively honor the strictest advertised timing directive, including
 # decimal Crawl-delay values unsupported by urllib's own convenience parser.
 for value in re.findall(r'(?im)^\s*crawl-delay\s*:\s*([^#\r\n]+)',policy):
  try:delay=float(value.strip())
  except ValueError:raise ValueError('Unrecognized robots Crawl-delay; review required')
  if not math.isfinite(delay) or delay<0:raise ValueError('Invalid robots Crawl-delay')
  interval=max(interval,delay)
 for value in re.findall(r'(?im)^\s*request-rate\s*:\s*([^#\r\n]+)',policy):
  match=re.fullmatch(r'\s*(\d+)\s*/\s*(\d+)\s*',value)
  if not match or int(match[1])<1 or int(match[2])<1:raise ValueError('Unrecognized robots Request-rate; review required')
  interval=max(interval,int(match[2])/int(match[1]))
 return {'note':'Allowed by published robots policy; strictest timing observed','parser':parser,'interval':interval}

class VisibleText(HTMLParser):
 def __init__(self):super().__init__();self.hidden=0;self.parts=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style','noscript'):self.hidden+=1
 def handle_endtag(self,tag):
  if tag in ('script','style','noscript'):self.hidden=max(0,self.hidden-1)
 def handle_data(self,text):
  if not self.hidden:self.parts.append(text)

def extract_names(body,format):
 if format=='json_names':
  names=json.loads(body).get('names')
  if not isinstance(names,list) or not all(isinstance(n,str) for n in names):raise ValueError('JSON source must contain a string names list')
  return list(dict.fromkeys(n.strip() for n in names if n.strip()))[:500]
 if format!='html_names':raise ValueError('Unsupported source format')
 parser=VisibleText();parser.feed(body)
 # Deliberately narrow: extract candidate binomials only. Never save page prose.
 return sorted(set(re.findall(r'\bAnthurium\s+[a-z][a-z-]{2,}(?![a-z-])',' '.join(parser.parts))))[:500]

def resolve_name(label,records):
 exact=[r for r in records if r['taxon_name'].casefold()==label.casefold()]
 accepted={r['plant_name_id']:r for r in records if r['taxon_status']=='Accepted'}
 targets={r['accepted_plant_name_id'] for r in exact if r.get('accepted_plant_name_id') in accepted}
 if len(targets)==1:
  id=next(iter(targets));target=accepted[id]
  return {'status':'exact WCVP name match; candidate only','accepted_name':target['taxon_name'],'accepted_id':id,'matched_statuses':sorted({r['taxon_status'] for r in exact}),'identity_verified':False}
 if exact:return {'status':'ambiguous or unresolved WCVP name','accepted_name':None,'accepted_id':None,'matched_statuses':sorted({r['taxon_status'] for r in exact}),'identity_verified':False}
 return {'status':'unresolved label; no exact WCVP match','accepted_name':None,'accepted_id':None,'matched_statuses':[],'identity_verified':False}

def candidates(rows,snapshot):
 output=[];seen=set()
 if not isinstance(rows,list) or len(rows)>2500:raise ValueError('Input must be a bounded list of at most 2500 candidates')
 for row in rows:
  if not isinstance(row,dict):raise ValueError('Each candidate must be an object')
  label=row.get('name','').strip();url=row.get('source_url','');date=row.get('observed_on','')
  if not label or len(label)>300:raise ValueError('Candidate names require 1–300 characters')
  public_https(url);datetime.date.fromisoformat(date)
  if datetime.date.fromisoformat(date)>datetime.datetime.now(datetime.timezone.utc).date():raise ValueError('Observation date cannot be in the future')
  key=(label,url,date)
  if key in seen:continue
  seen.add(key)
  output.append({'name_verbatim':label,'source_url':url,'observed_on':date,'review_status':'pending','source_role':'discovery lead only','taxonomy_resolution':resolve_name(label,snapshot['records']),'taxonomy_snapshot_version':snapshot['version'],'popularity':None,'popularity_note':'Occurrence is not a popularity measurement.','cross_evidence_promoted':False,'taxonomy_promoted':False})
 return output

def discover(config):
 if not config.get('enabled'):return [],{'status':'disabled; no source requests made'}
 sources=config.get('sources',[]);limit=config.get('max_pages_per_run',5);byte_limit=config.get('max_bytes_per_page',500000)
 if not isinstance(sources,list) or not 1<=limit<=10 or len(sources)>limit or not 1<=byte_limit<=1000000:raise ValueError('Discovery source or size bounds exceeded')
 minimum=interval_seconds(config.get('min_interval_seconds',5))
 rows=[];logs=[]
 for source in sources:
  url=source.get('url','');automated_source_allowed(url);public_https(source.get('terms_url',''))
  interval_seconds(source.get('min_interval_seconds',minimum))
  if source.get('terms_reviewed') is not True or not source.get('permission_note','').strip() or not source.get('id'):raise ValueError('Explicit reviewed source permission required')
  if source.get('format') not in ('html_names','json_names'):raise ValueError('Unsupported source format')
 # Validate every configured source before making any request. Cache robots per
 # origin; never issue a fresh robots request immediately before another page.
 gate=RequestGate();policies={}
 for source in sources:
  url=source['url'];origin=urlsplit(url).netloc.lower()
  requested=max(minimum,interval_seconds(source.get('min_interval_seconds',minimum)))
  if origin not in policies:policies[origin]=robots_policy(url,gate,requested)
  policy=policies[origin]
  if policy['parser'] and not policy['parser'].can_fetch(AGENT,url):raise ValueError('Robots policy disallows configured page')
  interval=max(requested,policy['interval']);raw=gate.fetch(url,byte_limit,interval);date=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
  names=extract_names(raw.decode('utf-8'),source['format'])
  rows.extend({'name':n,'source_url':url,'observed_on':date} for n in names)
  logs.append({'source_id':source['id'],'url':url,'observed_on':date,'response_sha256':hashlib.sha256(raw).hexdigest(),'robots':policy['note'],'effective_min_interval_seconds':interval,'terms_url':source['terms_url'],'permission_note':source['permission_note'],'names_found':len(names)})
 return rows,{'status':'bounded discovery completed; all candidates pending review','sources':logs}

def stage(rows,log,output):
 snapshot=json.loads((ROOT/'research/wcvp_anthurium_v16.json').read_text());items=candidates(rows,snapshot)
 payload={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pipeline':'discovery-only; separate from authoritative WCVP refresh','run':log,'candidates':items,'limitations':'No popularity ranking, identity verification, inferred pedigree, cross viability or automatic promotion.'}
 blob=(json.dumps(payload,indent=2,ensure_ascii=False)+'\n').encode();digest=hashlib.sha256(blob).hexdigest();output=Path(output);output.mkdir(parents=True,exist_ok=True)
 destination=output/(digest+'.json')
 with tempfile.NamedTemporaryFile(dir=output,delete=False) as f:tmp=Path(f.name);f.write(blob);f.flush();os.fsync(f.fileno())
 os.replace(tmp,destination)
 return destination,len(items)

def main():
 p=argparse.ArgumentParser(description=__doc__);group=p.add_mutually_exclusive_group(required=True);group.add_argument('--local-input',type=Path);group.add_argument('--source-config',type=Path);p.add_argument('--network',action='store_true');p.add_argument('--output',type=Path,default=ROOT/'data/discovery');a=p.parse_args()
 if a.local_input:rows=json.loads(a.local_input.read_text());log={'status':'local curated candidate import; no network requests','input_sha256':hashlib.sha256(a.local_input.read_bytes()).hexdigest()}
 else:
  config=json.loads(a.source_config.read_text())
  if config.get('enabled') and not a.network:p.error('Enabled sources require explicit --network opt-in')
  rows,log=discover(config)
 path,count=stage(rows,log,a.output);print(json.dumps({'artifact':str(path),'candidate_count':count,'run':log},indent=2))
if __name__=='__main__':main()
