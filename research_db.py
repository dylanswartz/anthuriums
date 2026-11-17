"""Versioned research schema and accession-level operations; no compatibility prediction."""
import hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RESEARCH_TABLES=['source_revisions','taxa','taxon_names','taxonomic_assertions','cultivars','accessions','cross_plans','pollen_lots','pollination_attempts','outcomes','evidence_claims','genomic_measurements','pedigree_edges','nomenclatural_claims','label_assertions','cross_hypotheses','fertility_assertions','cross_report_sources']
def migrate(db):
    db.execute('CREATE TABLE IF NOT EXISTS schema_migrations(version TEXT PRIMARY KEY,sha256 TEXT NOT NULL,applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
    for p in sorted((ROOT/'migrations').glob('*.sql')):
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        row=db.execute('SELECT sha256 FROM schema_migrations WHERE version=?',(p.stem,)).fetchone()
        if row:
            if row[0]!=digest: raise ValueError('Applied migration changed: '+p.name)
            continue
        try:
            db.executescript('BEGIN IMMEDIATE;\n'+p.read_text())
            db.execute('INSERT INTO schema_migrations(version,sha256) VALUES (?,?)',(p.stem,digest));db.commit()
        except Exception:db.rollback();raise

def ingest_research(db):
    raw=(ROOT/'research/wcvp_anthurium_v16.json').read_bytes();snap=json.loads(raw)
    rev='wcvp-v16-'+hashlib.sha256(raw).hexdigest()[:12]
    if db.execute('SELECT 1 FROM source_revisions WHERE id=?',(rev,)).fetchone():return
    with db:
        db.execute('INSERT INTO source_revisions VALUES (?,?,?,?,?)',(rev,'wcvp-v16','16',snap['retrieved'],hashlib.sha256(raw).hexdigest()))
        accepted={r['plant_name_id']:r for r in snap['records'] if r['taxon_status']=='Accepted'}
        for id,r in accepted.items():db.execute('INSERT OR IGNORE INTO taxa VALUES (?,?,?)',(id,r['taxon_rank'],r['taxon_name']))
        for r in snap['records']:
            db.execute('INSERT INTO taxon_names VALUES (?,?,?,?,?,?,?,?)',(rev+':'+r['plant_name_id'],r['accepted_plant_name_id'] if r['accepted_plant_name_id'] in accepted else None,r['taxon_name'],r['taxon_authors'],r['taxon_status'],r['accepted_plant_name_id'] or None,rev,json.dumps(r,ensure_ascii=False)))
        records=json.loads((ROOT/'research/cross_evidence.json').read_text())['records']+json.loads((ROOT/'research/additional_cross_evidence.json').read_text())['records']
        records += [r for r in json.loads((ROOT/'research/breeder_skg_tezula.json').read_text())['records'] if r['id'] in ('tezula-dreamweaver-necromancer','tezula-necromancer-dreamweaver')]
        for c in records:
            cid=c['id']
            if c.get('cultivar'):db.execute('INSERT OR IGNORE INTO cultivars VALUES (?,?,?,?,?,?,?)',(cid,c['cultivar'],cid,int(c['accepted']),int(c['established']),c.get('parentage_formula') or json.dumps({k:v for k,v in c.items() if 'parent' in k}),c.get('normalization_note','')))
            db.execute('INSERT OR IGNORE INTO evidence_claims VALUES (?,?,?,?,?,?,?,?,?,?)',(cid,'cultivar' if c.get('cultivar') else 'cross-report',cid,c['outcome'],'registrar-record' if c['evidence_type']=='registrar_record' else 'breeder-report',cid,None,c['source_url'],'Reported only; genetic parentage and fertility not verified.',None))
        for h in json.loads((ROOT/'research/historical_hybrid_formulas.json').read_text())['records']:
            db.execute('INSERT OR IGNORE INTO nomenclatural_claims VALUES (?,?,?,?,?,?,?,?,?)',(h['id'],h['accepted_id'] or h['id'],h['name'],h['status'],h['hybrid_formula_verbatim'],'unknown','wcvp-v16',h['publication'],0))
        for s in db.execute("SELECT * FROM species WHERE section_id IS NOT NULL OR section_note LIKE 'Unresolved%'").fetchall():
            db.execute('INSERT INTO taxonomic_assertions(taxon_id,predicate,value,source_id,status,notes) VALUES (?,?,?,?,?,?)',(s['id'],'section',s['section_id'] or 'unresolved',next((r['id'] for r in db.execute('SELECT id FROM sources WHERE url=?',(s['section_note'].split(' Source: ')[-1],))),None),'historical or unresolved',s['section_note']))

def ingest_labels(db):
    dossier=json.loads((ROOT/'research/retail_alias_research.json').read_text())
    with db:
        links={'FS':['vannini-fsrl','vannini-rlfs','vannini-fsrl-flowering','car0380','rooted-rarities-fsrl'],'RL':['vannini-fsrl','vannini-rlfs','vannini-fsrl-flowering','car0380','rooted-rarities-fsrl'],'FSRL':['vannini-fsrl','vannini-fsrl-flowering','car0380','rooted-rarities-fsrl'],'RLFS':['vannini-rlfs']}
        for original in dossier['aliases']:
            row=dict(original);row['related_report_ids']=links.get(row['label'],[])
            db.execute('INSERT OR REPLACE INTO label_assertions VALUES (?,?,?,?,?,?,?)',(row['label'],row['label'],row.get('expansion'),row['entity_type'],'retail-'+row['source'],row.get('note','')+' Source-specific label assertion; not a taxonomic synonym or authenticated clone identity.',json.dumps(row,ensure_ascii=False)))
        for row in db.execute("SELECT * FROM crosses WHERE source_id LIKE 'retail-%'").fetchall():
            db.execute('INSERT OR IGNORE INTO evidence_claims VALUES (?,?,?,?,?,?,?,?,?,?)',(row['id'],'cross-report',row['id'],row['outcome'],'breeder-report',row['source_id'],None,row['citation_detail'],row['uncertainty'],None))

def create_accession(db,id,label,taxon_id=None,cultivar_id=None,provenance=''):
    if not id.strip() or not label.strip():raise ValueError('Accession ID and label are required')
    with db:db.execute('INSERT INTO accessions(id,label,taxon_id,cultivar_id,provenance) VALUES (?,?,?,?,?)',(id,label,taxon_id,cultivar_id,provenance))

def create_plan(db,id,maternal,paternal,hypothesis=''):
    with db:db.execute('INSERT INTO cross_plans(id,maternal_accession_id,paternal_accession_id,hypothesis) VALUES (?,?,?,?)',(id,maternal,paternal,hypothesis))

def record_attempt(db,id,plan,when,pollen_lot=None,protocol='',controls='',inflorescence=None):
    import datetime
    datetime.date.fromisoformat(when)
    p=db.execute('SELECT paternal_accession_id FROM cross_plans WHERE id=?',(plan,)).fetchone()
    if not p:raise ValueError('Unknown cross plan')
    if pollen_lot:
        lot=db.execute('SELECT accession_id FROM pollen_lots WHERE id=?',(pollen_lot,)).fetchone()
        if not lot or lot[0]!=p[0]:raise ValueError('Pollen lot must belong to the planned paternal accession')
    with db:db.execute('INSERT INTO pollination_attempts(id,plan_id,attempted_on,pollen_lot_id,protocol,controls,maternal_inflorescence) VALUES (?,?,?,?,?,?,?)',(id,plan,when,pollen_lot,protocol,controls,inflorescence))

def record_outcome(db,id,attempt,stage,when,result,notes,numerator=None,denominator=None,unit=None):
    import datetime
    date=datetime.date.fromisoformat(when)
    parent=db.execute('SELECT attempted_on FROM pollination_attempts WHERE id=?',(attempt,)).fetchone()
    if not parent or date<datetime.date.fromisoformat(parent[0]):raise ValueError('Outcome must follow an existing attempt')
    if not notes.strip():raise ValueError('Describe observation and uncertainty')
    with db:
        db.execute('INSERT INTO outcomes VALUES (?,?,?,?,?,?,?,?)',(id,attempt,stage,when,result,numerator,denominator,unit))
        db.execute('INSERT INTO evidence_claims VALUES (?,?,?,?,?,?,?,?,?,?)',('outcome:'+id,'outcome',id,notes,'user-observation',None,None,'Local notebook','Unverified personal observation; identity and parentage not independently confirmed.',None))

def pedigree(db,id):
    return [dict(r) for r in db.execute('''WITH RECURSIVE lineage(child,parent,role,depth,path) AS (
    SELECT child_accession_id,parent_accession_id,role,1,'/'||child_accession_id||'/'||parent_accession_id||'/' FROM pedigree_edges WHERE child_accession_id=?
    UNION ALL SELECT e.child_accession_id,e.parent_accession_id,e.role,l.depth+1,l.path||e.parent_accession_id||'/' FROM pedigree_edges e JOIN lineage l ON e.child_accession_id=l.parent WHERE l.depth<64 AND instr(l.path,'/'||e.parent_accession_id||'/')=0)
    SELECT * FROM lineage ORDER BY depth,parent''',(id,))]

def ingest_literature(db):
    dossier=json.loads((ROOT/'research/published_open_pollination.json').read_text())
    with db:
        for src in dossier['sources']:
            db.execute('INSERT OR REPLACE INTO cross_report_sources VALUES (?,?,?)',(dossier['id'],src['id'],'Linked report family; not an independent experiment'))
            claim=dossier['fertility_claim'] if src['id'].endswith('1978') else dossier['reported_offspring']
            db.execute('INSERT OR REPLACE INTO evidence_claims VALUES (?,?,?,?,?,?,?,?,?,?)',(src['id']+'-indexed-claim','cross-report',dossier['id'],claim,'published-cross',src['id'],None,src['url'],dossier['access_level']+'; open pollination; paternal identity and functional fertility unverified; no graph eligibility.',None))

def ingest_grower_additions(db):
    records=json.loads((ROOT/'research/clarinervium_grower_reports.json').read_text())['records']+json.loads((ROOT/'research/palmstreet_seller_reports.json').read_text())['records']+json.loads((ROOT/'research/vegetative_clone_claims.json').read_text())['records']+json.loads((ROOT/'research/happiestplants_seller_report.json').read_text())['records']+json.loads((ROOT/'research/rochani_registration.json').read_text())['records']
    with db:
        for c in records:
            db.execute('INSERT OR REPLACE INTO cross_report_sources VALUES (?,?,?)',(c['id'],c['id'],'Source report; no independent corroboration claimed'))
            db.execute('INSERT OR REPLACE INTO evidence_claims VALUES (?,?,?,?,?,?,?,?,?,?)',(c['id'],c.get('claim_subject_type','cross-report'),c['id'],c['outcome'],c.get('claim_evidence_type','breeder-report'),c['id'],None,c.get('citation_detail',c['url']),c['uncertainty'],None))
