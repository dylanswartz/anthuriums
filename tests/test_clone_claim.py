import json,tempfile,unittest
from pathlib import Path
import app,research_db
class CloneClaimTests(unittest.TestCase):
 def test_nested_formula_is_a_vegetative_claim_with_unknown_roles(self):
  c=json.loads((app.ROOT/'research/vegetative_clone_claims.json').read_text())['records'][0]
  self.assertFalse(c['seed_grown']);self.assertEqual(c['propagation_method'],'vegetative');self.assertIsNone(c['event_date']);self.assertFalse(c['functional_fertility_verified'])
  p=c['pedigree_assertion'];self.assertFalse(p['direction_known']);self.assertEqual(len(p['parents']),2)
  for parent in p['parents']:self.assertFalse(parent['direction_known']);self.assertEqual(len(parent['components']),2)
  self.assertEqual(c['source_specific_expansions'][0]['expansion'],'Red Vein Dark Phoenix')
 def test_upgrade_is_idempotent_and_creates_no_sexual_outcome_or_taxon_edge(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'test.sqlite3'
   with app.connect(path) as db:
    db.executescript((app.ROOT/'schema.sql').read_text());research_db.migrate(db)
    old=json.loads((app.ROOT/'data/seed.json').read_text());old['crosses']=[c for c in old['crosses'] if not c['id'].startswith('plantess-')];old['sources']=[s for s in old['sources'] if not s['id'].startswith('plantess-')];app.import_seed(db,old)
   app.initialize(path);app.initialize(path)
   with app.connect(path) as db:
    c=dict(db.execute("SELECT * FROM crosses WHERE id='plantess-nested-pedigree-vegetative-clone'").fetchone())
    self.assertIsNone(c['maternal_id']);self.assertIsNone(c['paternal_id']);self.assertEqual(c['direction_known'],0);self.assertEqual(c['graph_eligible'],0);self.assertEqual(c['identity_qualified'],0)
    self.assertEqual(c['reported_endpoint'],'rooted vegetative clone listed')
    self.assertEqual(db.execute('SELECT count(*) FROM evidence_claims WHERE subject_id=?',(c['id'],)).fetchone()[0],1)
    self.assertEqual(tuple(db.execute('SELECT subject_type,evidence_type FROM evidence_claims WHERE subject_id=?',(c['id'],)).fetchone()),('pedigree-claim','unknown'))
    self.assertEqual(db.execute('SELECT count(*) FROM cross_report_sources WHERE cross_id=?',(c['id'],)).fetchone()[0],1)
    for table in ['outcomes','pedigree_edges','fertility_assertions']:self.assertEqual(db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
    self.assertEqual(db.execute("SELECT count(*) FROM label_assertions WHERE label='RVDP'").fetchone()[0],0)
    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
