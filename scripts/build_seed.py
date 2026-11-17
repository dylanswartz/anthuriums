"""Rebuild curated application records from the licensed, local WCVP snapshot."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
snapshot=json.loads((ROOT/'research/wcvp_anthurium_v16.json').read_text())
d={'sources':[{'id':'wcvp-v16','title':'WCVP v16 · Royal Botanic Gardens, Kew','url':snapshot['source'],'citation':snapshot['attribution']+' Version 16, published '+snapshot['published']+'. Adapted: filtered to accepted Anthurium species and linked name records.','accessed':snapshot['retrieved'],'license':snapshot['license']+' · https://creativecommons.org/licenses/by/3.0/'}],'sections':[],'species':[],'taxonomic_records':[],'crosses':[]}
accepted={r['plant_name_id']:r for r in snapshot['records'] if r['taxon_status']=='Accepted' and r['taxon_rank']=='Species'}
for id,r in accepted.items():
    d['species'].append({'id':id,'name':r['taxon_name'],'author':r['taxon_authors'],'distribution':r['geographic_area'],'summary':' · '.join(v for v in [r['lifeform_description'],r['climate_description']] if v),'section_id':None,'section_note':'Not curated. WCVP source does not provide section placement.'})
for r in snapshot['records']:
    aid=r['accepted_plant_name_id']
    if aid not in accepted:continue
    note=' '.join(v for v in [r['taxon_authors'],r['place_of_publication']+r['volume_and_page'],r['first_published'],r['nomenclatural_remarks']] if v)
    if r['powo_id']:note+=' | POWO identifier: '+r['powo_id']
    d['taxonomic_records'].append({'id':r['plant_name_id'],'species_id':aid,'name':r['taxon_name'],'status':r['taxon_status'],'source_id':'wcvp-v16','note':note})
# Curated additions use the application's normalized schema, retain source-level status.
extra=ROOT/'research/curated_app.json'
if extra.exists():
    additions=json.loads(extra.read_text())
    for t in ['sources','sections','crosses']:d[t].extend(additions.get(t,[]))
    for update in additions.get('species_updates',[]):
        target=next(s for s in d['species'] if s['name']==update['name']);target.update(update)
(ROOT/'data/seed.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print({k:len(v) for k,v in d.items()})
