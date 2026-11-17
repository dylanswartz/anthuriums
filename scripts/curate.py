"""Normalize cited facts; preserve ambiguity, nomenclature, and source-specific status."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
read=lambda f:json.loads((root/'research'/f).read_text())
w=read('wcvp_anthurium_v16.json');ids={r['taxon_name']:r['plant_name_id'] for r in w['records'] if r['taxon_status']=='Accepted' and r['taxon_rank']=='Species'}
a={'sources':[],'sections':[],'crosses':[],'species_updates':[]}
tezula=[r for r in read('breeder_skg_tezula.json')['records'] if r['id'] in ('tezula-dreamweaver-necromancer','tezula-necromancer-dreamweaver')]
for c in read('cross_evidence.json')['records']+read('additional_cross_evidence.json')['records']+tezula:
 title=c.get('cultivar',c['id'].replace('-',' ').title());registry=c['evidence_type']=='registrar_record'
 status=(' Registry accepted: '+('yes' if c['accepted'] else 'no')+'; established: '+('yes' if c['established'] else 'no')+'.') if registry else ''
 a['sources'].append({'id':c['id'],'title':('IAS cultivar registry · ' if registry else 'First-party report · ')+title,'url':c['source_url'],'citation':'Curated factual relationship record for '+title+'.'+status,'accessed':'2026-11-17','license':'No open reuse license verified; factual summary only; no images or copied description.'})
 parents=c.get('parents',[c.get('seed_parent'),c.get('pollen_parent')]);m=ids.get(parents[0]);p=ids.get(parents[1]);direction=bool(c.get('seed_parent') and c.get('pollen_parent'))
 details=' | '.join(str(v) for v in [c.get('parentage_formula'),c.get('parentage_note'),c.get('source_date') and 'Source date: '+c['source_date'],c.get('cross_year') and 'Cross year reported: '+str(c['cross_year']),c.get('source_seed_parent_verbatim') and 'Raw seed-parent spelling: '+c['source_seed_parent_verbatim'],c.get('source_pollen_parent_verbatim') and 'Pollen alternatives: '+c['source_pollen_parent_verbatim'],'Parent labels: '+str(parents)] if v)
 a['crosses'].append({'id':c['id'],'maternal_id':m,'paternal_id':p,'maternal_label':parents[0],'paternal_label':parents[1] or ' OR '.join(c.get('pollen_parent_candidates',[])) or None,'direction_known':int(direction),'evidence_type':'Registrar record · breeder report' if registry else 'First-party grower report','outcome':title+': '+c['outcome']+'.'+status,'uncertainty':'Reported parentage, not a controlled experiment or genetic verification. Fertility unknown; no success rate or reciprocal inference. '+c.get('normalization_note','')+' '+c['direction']+'.','source_id':c['id'],'citation_detail':details})
# Deduplicate hybrid names by accepted name ID. Retain all raw 43 records separately.
groups={}
for h in read('historical_hybrid_formulas.json')['records']:groups.setdefault(h['accepted_id'] or h['id'],[]).append(h)
for group,items in groups.items():
 h=next((x for x in items if x['id']==group),items[0]);formula=h['hybrid_formula_verbatim'];parts=re.fullmatch(r'A\. ([a-z]+) × A\. ?([a-z]+)',formula)
 m,p=(ids.get('Anthurium '+parts[1]),ids.get('Anthurium '+parts[2])) if parts else (None,None)
 a['crosses'].append({'id':'wcvp-formula-'+group,'maternal_id':m,'paternal_id':p,'direction_known':0,'evidence_type':'Historical taxonomic hybrid formula','outcome':h['name']+': '+formula+'. Nomenclatural status: '+h['status']+'.','uncertainty':'Not a controlled cross experiment or verified viable offspring. Direction and fertility unknown. '+str(len(items))+' name record(s) in this accepted-name group; synonyms are not independent corroboration.','source_id':'wcvp-v16','citation_detail':h['publication']+' | '+h['source_url']})
sections=read('section_evidence.json');seen=set()
for i,s in enumerate(sections['assignments']):
 sid='section-source-'+str(i)
 a['sources'].append({'id':sid,'title':s['framework'],'url':s['source_url'],'citation':s['framework']+'; '+str(s['year'] or 'undated')+'. '+s['confidence']+'. Current classification not verified.','accessed':'2026-11-17','license':'Source terms apply; curated assignment fact only.'})
 if s['section'] not in seen:
  a['sections'].append({'id':s['section'],'name':s['section'],'description':'Source-specific historical/traditional grouping. Current classification and monophyly not asserted; no compatibility inference.','source_id':sid,'status':'Historical / traditional · not current consensus'});seen.add(s['section'])
 a['species_updates'].append({'name':s['name'],'section_id':s['section'],'section_note':s['framework']+' ('+str(s['year'] or 'undated')+'); '+s['confidence']+'. Current classification not verified. Source: '+s['source_url']})
for s in sections['unresolved']:a['species_updates'].append({'name':s['name'],'section_id':None,'section_note':'Unresolved: '+s['reason']+(' Source: '+s['source_url'] if s.get('source_url') else ' No definitive primary revision curated.')})
# Retail/breeder labels retain their exact source-level identities; no alias-to-taxon promotion.
retail=read('retail_alias_research.json')
for r in retail['sources']:
 a['sources'].append({'id':'retail-'+r['id'],'title':r.get('author') or r['id'],'url':r['url'],'citation':r['kind']+'. '+r.get('date_note','')+' Curated factual metadata only.','accessed':retail['reviewed_at'],'license':r['rights']})
fs="Anthurium papillilaminum 'Fort Sherman'";rl="Anthurium papillilaminum 'Ralph Lynam'";fsrl='Anthurium papillilaminum (Fort Sherman x Ralph Lynam)'
selected={
 'vannini-fsrl':(fs,rl,0),
 'vannini-rlfs':(rl,fs,0),
 'vannini-fsrl-flowering':(fs,rl,0),
 'car0380':('Anthurium magnificum',fsrl,0),
 'car0280':('Anthurium antolakii','Anthurium luxurians',1),
 'rooted-rarities-fsrl':(fsrl,'(dressleri x carlablackiae) x antolakii / BVEP',1)
}
for r in retail['records']:
 if r['id'] not in selected:continue
 m,p,direction=selected[r['id']]
 # Pure-species mapping only for the explicitly identified CAR-0280 seed/pollen record.
 pure=r['id']=='car0280'
 a['crosses'].append({'id':r['id'],'maternal_id':ids.get(m) if pure else None,'paternal_id':ids.get(p) if pure else None,'maternal_label':m,'paternal_label':p,'direction_known':direction,'evidence_type':'Retailer-attributed grower report' if r.get('reporter') else 'First-party grower report','outcome':r['id']+': '+r['outcome']+'.','uncertainty':'Source-reported identity and outcome, not genetic verification. '+r.get('note','')+' '+r['direction']+'. Fertility and success rates unknown. Clone/line identities are not authenticated by the label.','source_id':'retail-'+r['source'],'citation_detail':'Raw formula/labels: '+str(r.get('formula') or [r.get('seed_parent'),r.get('pollen_parent')])+' | Breeder: '+r.get('breeder','see cited author')+' | Reporter: '+r.get('reporter','source author')})
# Research-method citations support interpretation rules, not imported outcome rows.
for sid,title,url,citation in [
 ('method-s1','Marutani, Sheffer & Kamemoto · 1993','https://doi.org/10.1002/j.1537-2197.1993.tb13772.x','Cytological Analysis of Anthurium andraeanum (Araceae), Its Related Taxa and Their Hybrids. American Journal of Botany 80:93–103. Accession, parental-role and endpoint interpretation; numerical tables not imported.'),
 ('method-s2','Camelo et al. · 2026','https://www.mdpi.com/2223-7747/15/6/866','Plants 15:866. Phylogenomic neighborhood context; limited species/accession sampling is not a compatibility dataset.'),
 ('method-s3','Nascimento et al. · 2019','https://www.scielo.br/j/gmb/a/bQVywrCJGLW3CnszHYFJhmK/?lang=en','Sample-scoped Anthurium cytology. Species labels do not assign accession cytotypes; no measured counts imported.'),
 ('method-s4','Tiffin, Olson & Moyle · 2001','https://cbs.umn.edu/sites/cbs.umn.edu/files/migrated-files/downloads/Tiffinetal_ProcB_2001.pdf','Comparative reciprocal crossing study. Direction and developmental stage must be retained; no Anthurium probability estimates derived.'),
 ('method-s5','Carlsen & Croat · 2013','https://doi.org/10.1600/036364413X670287','Anthurium molecular phylogeny. Unresolved placements and traditional sections are not a crossability model.')]:
 a['sources'].append({'id':sid,'title':title,'url':url,'citation':citation,'accessed':'2026-11-17','license':'Source-specific publication terms; citation and original factual summary only, no paper/table reproduction.'})
# Affirmative endpoint classification is curated explicitly; missing fields never
# imply successful offspring. Registry acceptance alone is not graph evidence.
seedling_reports={'steves-forgetii-crystallinum','docblock-black-widow-michelle','tezula-dreamweaver-necromancer','tezula-necromancer-dreamweaver','vannini-fsrl','vannini-rlfs','car0380','car0280'}
for c in a['crosses']:
 c.update(reported_result='unknown',reported_endpoint='unknown',identity_qualified=int(bool(c['maternal_id'] and c['paternal_id'])),graph_eligible=0)
 if c['id'] in seedling_reports:c.update(reported_result='reported',reported_endpoint='seedling growth',graph_eligible=c['identity_qualified'])
 elif c['id']=='vannini-fsrl-flowering':c.update(reported_result='reported',reported_endpoint='flowering',graph_eligible=c['identity_qualified'])
 elif c['id']=='rooted-rarities-fsrl':c.update(reported_result='reported',reported_endpoint='grown plant offered')
 elif c['evidence_type'].startswith('Registrar') and c['id']!='ias-giant-claire':c.update(reported_result='reported',reported_endpoint='reported propagated cultivar')
 if c['id']=='ias-smaug':
  c.update(reported_result='reported',reported_endpoint='seedling growth',graph_eligible=c['identity_qualified'])
  c['citation_detail']+=' | Source rechecked 2026-11-17: registrar describes selection as a young seedling; seed/pollen roles explicit. Reported identity, not genetic verification; fertility unknown.'
 if c['id']=='ias-medusa':
  c.update(reported_result='reported',reported_endpoint='flowering',graph_eligible=c['identity_qualified'])
  c['citation_detail']+=' | Source rechecked 2026-11-17: growing plant, inflorescences and sibling distinctions described. Germination and functional fertility not established.'
  c['uncertainty']=c['uncertainty'].replace('Registry misspells forgetti in structured field, narrative says forgetii; WCVP accepts forgetii. Preserve both.','Earlier curated snapshot recorded forgetti; current source recheck uses forgetii. Earlier raw spelling is retained as dated snapshot metadata.')
 if c['id']=='ias-giant-claire':
  c['uncertainty']=c['uncertainty'].replace('Seed field spelling differs from correctly spelled base-species field. Preserve raw source.','Earlier curated snapshot recorded faustinomirandae; current source recheck uses faustomirandae. Raw earlier spelling is retained as snapshot metadata.')
# Access-limited literature is searchable but never an empirical inference edge.
lit=read('published_open_pollination.json')
for src in lit['sources']:
 a['sources'].append({'id':src['id'],'title':src['title'],'url':src['url'],'citation':src['citation']+' '+lit['access_level']+'. '+src['access_note'],'accessed':lit['reviewed_at'],'license':'Source-specific publication terms; original factual summary and citation only.'})
a['crosses'].append({'id':lit['id'],'maternal_id':ids[lit['seed_parent']],'paternal_id':ids[lit['attributed_pollen_parent']],'maternal_label':lit['seed_parent']+' (documented seed mother)','paternal_label':lit['attributed_pollen_parent']+' (attributed pollen parent)','direction_known':0,'evidence_type':'Published open-pollination report · abstract/index only','outcome':lit['reported_offspring']+' '+lit['fertility_claim'],'uncertainty':'Open pollination: seed mother documented in indexed abstract; pollen parent attributed, not controlled or genetically confirmed. Title order is not reciprocal evidence. Functional fertility and numerical outcomes are not verified. Excluded from the inference graph pending full-methods review. '+lit['independence'],'source_id':lit['sources'][0]['id'],'citation_detail':lit['spelling_alignment']+' Original publication spelling: '+lit['original_spelling']+'. '+lit['sources'][1]['citation']+' '+lit['sources'][1]['access_note'],'reported_result':'reported','reported_endpoint':'reported offspring (abstract only)','identity_qualified':0,'graph_eligible':0,'access_level':lit['access_level'],'report_family_id':lit['report_family_id']})
# Curated grower reports preserve disputed identity and compound parents.
for c in read('clarinervium_grower_reports.json')['records']+read('palmstreet_seller_reports.json')['records']+read('vegetative_clone_claims.json')['records']+read('happiestplants_seller_report.json')['records']+read('rochani_registration.json')['records']:
 a['sources'].append({'id':c['id'],'title':c['title'],'url':c['url'],'citation':c['title']+'. '+('Published '+c['published']+'. ' if c['published'] else 'Publication date not stated. ')+c['access_level']+'.','accessed':c['retrieved'],'license':'No open reuse license verified; factual paraphrase and citation only; no copied images or prose.'})
 a['crosses'].append({'id':c['id'],'maternal_id':ids.get(c['maternal_taxon']),'paternal_id':ids.get(c['paternal_taxon']),'maternal_label':c['maternal_label'],'paternal_label':c['paternal_label'],'direction_known':c['direction_known'],'evidence_type':c['evidence_type'],'outcome':c['outcome'],'uncertainty':c['uncertainty'],'source_id':c['id'],'citation_detail':c.get('citation_detail','Source title: '+c['title'])+' | Original URL: '+c['url'],'reported_result':'reported','reported_endpoint':c['reported_endpoint'],'identity_qualified':c['identity_qualified'],'graph_eligible':c['graph_eligible'],'access_level':c['access_level'],'report_family_id':c['id']})
(root/'research/curated_app.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
