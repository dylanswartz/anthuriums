import copy,json,sqlite3,tempfile,unittest
from pathlib import Path
import app,research_db
from scripts.refresh_wcvp import validate,stage
class DatabaseTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'test.sqlite3';app.initialize(self.path);self.db=app.connect(self.path)
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def test_real_seed_integrity_and_names(self):
  self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0],'ok');self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(),[])
  self.assertEqual(self.db.execute('SELECT count(*) FROM species').fetchone()[0],1460)
  self.assertEqual(self.db.execute('SELECT count(*) FROM taxon_names').fetchone()[0],2177)
  self.assertEqual(self.db.execute('SELECT count(*) FROM nomenclatural_claims').fetchone()[0],43)
 def test_idempotent_migration(self):
  research_db.migrate(self.db);research_db.ingest_research(self.db)
  self.assertEqual(self.db.execute('SELECT count(*) FROM source_revisions').fetchone()[0],1)
 def test_registry_flags_and_types(self):
  self.assertEqual(tuple(self.db.execute("SELECT registry_accepted,registry_established FROM cultivars WHERE id='ias-giant-claire'").fetchone()),(1,1))
  self.assertEqual(self.db.execute("SELECT evidence_type FROM evidence_claims WHERE id='steves-forgetii-crystallinum'").fetchone()[0],'breeder-report')
  self.assertIsNone(self.db.execute("SELECT maternal_id FROM crosses WHERE id='ias-amy'").fetchone()[0])
  self.assertIsNone(self.db.execute("SELECT paternal_id FROM crosses WHERE id='ias-mikes-goliath'").fetchone()[0])
 def test_conflicting_sections_unassigned(self):
  for name in ['Anthurium clarinervium','Anthurium pallidiflorum']:
   row=self.db.execute('SELECT section_id,section_note FROM species WHERE name=?',(name,)).fetchone();self.assertIsNone(row[0]);self.assertTrue(row[1].startswith('Unresolved:'))
 def fixture_attempt(self):
  research_db.create_accession(self.db,'fixture-a','Synthetic accession A','10810');research_db.create_accession(self.db,'fixture-b','Synthetic unresolved trade label')
  research_db.create_plan(self.db,'fixture-plan','fixture-a','fixture-b','Test fixture only')
  research_db.record_attempt(self.db,'fixture-attempt','fixture-plan','2026-01-01')
 def test_attempt_outcome_not_viability(self):
  self.fixture_attempt();research_db.record_outcome(self.db,'fixture-fruit','fixture-attempt','fruit set','2026-02-01','observed','Synthetic fixture; no hybridity established',1,2,'inflorescences')
  self.assertEqual(self.db.execute('SELECT count(*) FROM outcomes').fetchone()[0],1)
  self.assertEqual(self.db.execute('SELECT stage FROM outcomes').fetchone()[0],'fruit set')
  self.assertEqual(self.db.execute('SELECT censored FROM pollination_attempts').fetchone()[0],1)
  self.assertIsNone(self.db.execute("SELECT taxon_id FROM accessions WHERE id='fixture-b'").fetchone()[0])
 def test_invalid_outcome_rolls_back(self):
  self.fixture_attempt()
  with self.assertRaises(sqlite3.IntegrityError):research_db.record_outcome(self.db,'bad','fixture-attempt','germination','2026-02-01','observed','fixture',3,2,'seeds')
  self.assertEqual(self.db.execute('SELECT count(*) FROM outcomes').fetchone()[0],0)
  with self.assertRaises(ValueError):research_db.record_outcome(self.db,'early','fixture-attempt','germination','2025-02-01','observed','fixture')
 def test_foreign_keys_and_pollen_identity(self):
  with self.assertRaises(sqlite3.IntegrityError):research_db.create_accession(self.db,'bad','Bad','nonexistent')
  self.fixture_attempt()
  with self.db:self.db.execute("INSERT INTO pollen_lots VALUES ('lot','fixture-a','2026-01-01','dry')")
  with self.assertRaises(ValueError):research_db.record_attempt(self.db,'bad-lot','fixture-plan','2026-01-01','lot')
 def test_pedigree_recursive_and_cycle(self):
  self.fixture_attempt();research_db.create_accession(self.db,'fixture-child','Child')
  with self.db:
   self.db.execute("INSERT INTO evidence_claims VALUES ('fixture-claim','accession','fixture-child','Synthetic pedigree','user-observation',NULL,NULL,'','Unverified',NULL)")
   self.db.execute("INSERT INTO pedigree_edges VALUES ('fixture-child','fixture-a','maternal','fixture-attempt','fixture-claim')")
  self.assertEqual(research_db.pedigree(self.db,'fixture-child')[0]['parent'],'fixture-a')
  with self.assertRaises(sqlite3.IntegrityError):
   with self.db:self.db.execute("INSERT INTO pedigree_edges VALUES ('fixture-a','fixture-child','unknown',NULL,'fixture-claim')")
 def test_import_is_transactional(self):
  seed={k:[] for k in app.TABLES};seed['species']=[{'id':'fixture-temp','name':'Fixture'},{'id':'fixture-bad','name':'Bad','section_id':'missing'}]
  with self.assertRaises(sqlite3.IntegrityError):app.import_seed(self.db,seed)
  self.assertIsNone(self.db.execute("SELECT id FROM species WHERE id='fixture-temp'").fetchone())
 def test_refresh_last_good_survives_bad_candidate(self):
  snap=json.loads((app.ROOT/'research/wcvp_anthurium_v16.json').read_text());output=Path(self.tmp.name)/'refresh';stage(snap,output);before=(output/'latest.json').read_bytes()
  bad=copy.deepcopy(snap);bad['records']=[]
  with self.assertRaises(ValueError):stage(bad,output)
  self.assertEqual((output/'latest.json').read_bytes(),before)
 def test_section_assertion_cites_exact_species_source(self):
  row=self.db.execute("SELECT s.url FROM taxonomic_assertions a JOIN sources s ON a.source_id=s.id WHERE a.taxon_id='10882'").fetchone()
  self.assertIn('crystallinum.php',row[0])
 def test_refresh_rejects_duplicate_ids_and_unapproved_network(self):
  from scripts.refresh_wcvp import network_snapshot
  snap=json.loads((app.ROOT/'research/wcvp_anthurium_v16.json').read_text());snap['records'].append(snap['records'][0])
  with self.assertRaises(ValueError):validate(snap)
  with self.assertRaises(ValueError):network_snapshot({'url':'https://example.com/not-approved'})
 def test_http_endpoints_and_read_only(self):
  import threading
  from urllib.request import urlopen,Request
  from urllib.error import HTTPError
  old=app.DB;app.DB=self.path
  server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   base='http://127.0.0.1:'+str(server.server_port)
   for path in ['/','/app.js','/style.css','/api/data','/api/export']:
    with urlopen(base+path) as r:
     self.assertEqual(r.status,200);body=r.read()
     if path=='/api/export':self.assertEqual(len(json.loads(body)['research']['taxon_names']),2177)
   with self.assertRaises(HTTPError) as e:urlopen(Request(base+'/api/observations',data=b'{}'))
   self.assertEqual(e.exception.code,405)
   with self.assertRaises(HTTPError) as e:urlopen(base+'/../schema.sql')
   self.assertEqual(e.exception.code,404)
  finally:server.shutdown();server.server_close();thread.join();app.DB=old
 def test_robots_absence_disallow_and_uncertain_errors(self):
  from unittest.mock import patch
  from urllib.error import HTTPError
  from scripts.refresh_wcvp import check_robots
  for code in [404,410]:
   with patch('scripts.refresh_wcvp.fetch',side_effect=HTTPError('x',code,'',{},None)):
    self.assertIn('No robots policy',check_robots('https://sftp.kew.org/robots.txt'))
  with patch('scripts.refresh_wcvp.fetch',return_value=b'User-agent: *\nDisallow: /'):
   with self.assertRaises(ValueError):check_robots('https://sftp.kew.org/robots.txt')
  with patch('scripts.refresh_wcvp.fetch',side_effect=HTTPError('x',503,'',{},None)):
   with self.assertRaises(HTTPError):check_robots('https://sftp.kew.org/robots.txt')
 def test_tezula_explicit_reciprocals_preserve_trade_lines(self):
  rows=self.db.execute("SELECT * FROM crosses WHERE id IN ('tezula-dreamweaver-necromancer','tezula-necromancer-dreamweaver') ORDER BY id").fetchall()
  self.assertEqual(len(rows),2)
  self.assertEqual(rows[0]['maternal_label'],rows[1]['paternal_label'])
  for row in rows:
   self.assertEqual(row['direction_known'],1);self.assertIsNone(row['maternal_id']);self.assertIsNone(row['paternal_id']);self.assertIn('per-direction counts not separated',row['outcome'])
   self.assertEqual(self.db.execute('SELECT evidence_type FROM evidence_claims WHERE id=?',(row['id'],)).fetchone()[0],'breeder-report')
 def test_label_assertions_and_hybrid_parent_scope(self):
  self.assertEqual(self.db.execute('SELECT count(*) FROM label_assertions').fetchone()[0],10)
  fsrl=self.db.execute("SELECT expansion FROM label_assertions WHERE label='FSRL'").fetchone()[0]
  rlfs=self.db.execute("SELECT expansion FROM label_assertions WHERE label='RLFS'").fetchone()[0];self.assertNotEqual(fsrl,rlfs)
  self.assertEqual(json.loads(self.db.execute("SELECT raw_json FROM label_assertions WHERE label='RLFS'").fetchone()[0])['related_report_ids'],['vannini-rlfs'])
  row=self.db.execute("SELECT maternal_id,paternal_id,direction_known FROM crosses WHERE id='car0380'").fetchone();self.assertEqual(tuple(row),(None,None,0))
  self.assertEqual(self.db.execute('SELECT count(*) FROM cross_hypotheses').fetchone()[0],0)
  self.assertEqual(self.db.execute('SELECT count(*) FROM fertility_assertions').fetchone()[0],0)
 def test_existing_database_upgrade_preserves_research(self):
  legacy=Path(self.tmp.name)/'legacy.sqlite3';db=app.connect(legacy);db.executescript((app.ROOT/'schema.sql').read_text());research_db.migrate(db)
  seed=json.loads((app.ROOT/'data/seed.json').read_text())
  seed['sources']=[r for r in seed['sources'] if not r['id'].startswith('retail-')]
  seed['crosses']=[r for r in seed['crosses'] if not r['source_id'].startswith('retail-')]
  app.import_seed(db,seed)
  with db:
   db.execute("INSERT INTO taxa VALUES ('legacy-taxon','Species','Synthetic fixture taxon')")
   db.execute("INSERT INTO accessions(id,label,taxon_id) VALUES ('private-fixture','Synthetic preserved record','legacy-taxon')")
   db.execute("INSERT INTO observations(maternal_id,paternal_id,observed_on,stage,notes) VALUES ('10999','329822','2026-01-01','fruit set','Synthetic upgrade preservation test')")
  db.close();app.initialize(legacy);app.initialize(legacy)
  with app.connect(legacy) as upgraded:
   self.assertEqual(upgraded.execute('PRAGMA foreign_key_check').fetchall(),[])
   self.assertEqual(upgraded.execute("SELECT count(*) FROM sources WHERE id LIKE 'retail-%'").fetchone()[0],6)
   self.assertEqual(upgraded.execute('SELECT count(*) FROM label_assertions').fetchone()[0],10)
   self.assertEqual(upgraded.execute("SELECT label FROM accessions WHERE id='private-fixture'").fetchone()[0],'Synthetic preserved record')
   self.assertEqual(upgraded.execute('SELECT count(*) FROM observations').fetchone()[0],1)
 def test_graph_eligibility_is_affirmatively_curated(self):
  self.assertEqual(tuple(self.db.execute("SELECT reported_result,reported_endpoint,graph_eligible FROM crosses WHERE id='ias-medusa'").fetchone()),('reported','flowering',1))
  self.assertEqual(tuple(self.db.execute("SELECT reported_result,reported_endpoint,graph_eligible FROM crosses WHERE id='steves-forgetii-crystallinum'").fetchone()),('reported','seedling growth',1))
  self.assertEqual(self.db.execute("SELECT count(*) FROM crosses WHERE evidence_type LIKE '%formula%' AND graph_eligible=1").fetchone()[0],0)
  self.assertEqual(self.db.execute("SELECT graph_eligible FROM crosses WHERE id='ias-mikes-goliath'").fetchone()[0],0)
  self.assertEqual(tuple(self.db.execute("SELECT reported_endpoint,graph_eligible FROM crosses WHERE id='ias-smaug'").fetchone()),('seedling growth',1))
  self.assertEqual(tuple(self.db.execute("SELECT reported_endpoint,graph_eligible FROM crosses WHERE id='ias-giant-claire'").fetchone()),('unknown',0))
 def test_no_personal_seed_data(self):
  self.assertEqual(self.db.execute('SELECT count(*) FROM observations').fetchone()[0],0);self.assertEqual(self.db.execute('SELECT count(*) FROM accessions').fetchone()[0],0)
if __name__=='__main__':unittest.main()
