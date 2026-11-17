#!/usr/bin/env python3
"""Stage an auditable WCVP snapshot; never silently replace the research database."""
import argparse,csv,datetime,hashlib,io,json,os,tempfile,zipfile
from pathlib import Path
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.robotparser import RobotFileParser
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
ALLOWED='https://sftp.kew.org/pub/data-repositories/WCVP/wcvp.zip'
class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,*args):raise ValueError('Redirect rejected; review source configuration')
def fetch(url,limit):
 with build_opener(NoRedirect).open(Request(url,headers={'User-Agent':'AnthuriumAtlasResearch/1.0 (curated botanical research; monthly bulk refresh)'}),timeout=90) as r:
  data=r.read(limit+1)
  if len(data)>limit:raise ValueError('Download exceeds configured limit')
  return data

def validate(snapshot,minimum=1500):
 rows=snapshot.get('records',[])
 if len(rows)<minimum:raise ValueError('Suspiciously small Anthurium snapshot')
 ids=set()
 required={'plant_name_id','taxon_name','taxon_status','taxon_rank','accepted_plant_name_id','genus'}
 for r in rows:
  if required-set(r) or r['genus']!='Anthurium':raise ValueError('Schema or genus mismatch')
  if not r['plant_name_id'] or r['plant_name_id'] in ids:raise ValueError('Duplicate or absent name ID')
  ids.add(r['plant_name_id'])
 if sum(r['taxon_status']=='Accepted' and r['taxon_rank']=='Species' for r in rows)<minimum//2:raise ValueError('Accepted-species coverage collapsed')
 return rows

def stage(snapshot,output):
 rows=validate(snapshot);output=Path(output);output.mkdir(parents=True,exist_ok=True)
 raw=(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n').encode();sha=hashlib.sha256(raw).hexdigest()
 target=output/(sha+'.json')
 old=json.loads((ROOT/'research/wcvp_anthurium_v16.json').read_text())
 before={r['plant_name_id']:r for r in old['records']};after={r['plant_name_id']:r for r in rows}
 report={'snapshot':target.name,'sha256':sha,'retrieved':snapshot['retrieved'],'version':snapshot.get('version'),'added':sorted(after.keys()-before.keys()),'removed':sorted(before.keys()-after.keys()),'changed':[k for k in before.keys()&after.keys() if before[k]!=after[k]],'records':len(rows),'status':'validated candidate; requires taxonomy review before database promotion','previous_snapshot_preserved':True}
 # Immutable snapshot first, atomic pointer last. Any failure leaves prior pointer usable.
 with tempfile.NamedTemporaryFile(dir=output,delete=False) as f:
  tmp=Path(f.name);f.write(raw);f.flush();os.fsync(f.fileno())
 os.replace(tmp,target)
 current=output/'latest.json'
 if current.exists():(output/'last-good.json').write_bytes(current.read_bytes())
 with tempfile.NamedTemporaryFile(dir=output,mode='w',delete=False) as f:
  tmp=Path(f.name);json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(tmp,current)
 return report

def check_robots(url):
 try:policy=fetch(url,1000000).decode()
 except HTTPError as error:
  if error.code in (404,410):return 'No robots policy published (HTTP '+str(error.code)+')'
  raise
 robot=RobotFileParser();robot.parse(policy.splitlines())
 if not robot.can_fetch('AnthuriumAtlasResearch',ALLOWED):raise ValueError('Source robots disallows download')
 return 'Allowed by published robots policy'

def network_snapshot(config):
 if config.get('url')!=ALLOWED or config.get('robots_url')!='https://sftp.kew.org/robots.txt' or not config.get('terms_reviewed') or config.get('license')!='CC BY 3.0':raise ValueError('Source not explicitly approved')
 check_robots(config['robots_url'])
 blob=fetch(ALLOWED,config['max_download_bytes']);digest=hashlib.sha256(blob).hexdigest()
 with zipfile.ZipFile(io.BytesIO(blob)) as z:
  files=[i for i in z.infolist() if i.filename.rsplit('/',1)[-1]=='wcvp_names.csv']
  if len(files)!=1:raise ValueError('Expected one wcvp_names.csv; source format changed')
  info=files[0]
  if info.file_size>config['max_uncompressed_bytes']:raise ValueError('Uncompressed file too large')
  with z.open(info) as f:rows=[r for r in csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig'),delimiter='|') if r.get('genus')=='Anthurium']
 today=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
 result={'source':config['source'],'download_url':ALLOWED,'archive_sha256':digest,'license':config['license'],'version':'download-'+today+'-'+digest[:12],'published':'not asserted; inspect publisher release metadata','retrieved':today,'attribution':'Govaerts, R.; Board of Trustees of the Royal Botanic Gardens, Kew. World Checklist of Vascular Plants.','records':rows}
 validate(result,config['minimum_anthurium_records']);return result

def main():
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--local-snapshot',type=Path);g.add_argument('--network-config',type=Path);p.add_argument('--output',type=Path,default=ROOT/'data/refresh');a=p.parse_args()
 snap=json.loads(a.local_snapshot.read_text()) if a.local_snapshot else network_snapshot(json.loads(a.network_config.read_text()))
 print(json.dumps(stage(snap,a.output),indent=2))
if __name__=='__main__':main()
