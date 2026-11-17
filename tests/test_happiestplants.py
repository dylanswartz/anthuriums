import json,tempfile,unittest
from pathlib import Path
import app
class HappiestPlantsTests(unittest.TestCase):
 def test_outer_direction_nested_parent_and_attribution(self):
  c=json.loads((app.ROOT/'research/happiestplants_seller_report.json').read_text())['records'][0]
  self.assertEqual(c['seller'],'Happiest Plants');self.assertIn('not breeder-direct',c['breeder_attribution']['scope']);self.assertEqual(c['breeder_attribution']['name'],'Eddy Pranoto')
  self.assertTrue(c['pedigree_assertion']['direction_known']);p=c['pedigree_assertion']['pollen_parent'];self.assertFalse(p['direction_known']);self.assertEqual(p['label'],'(BVEP × Dorito Portillae)');self.assertEqual(p['components'][0]['source_alternative_label'],'Antolakii')
  self.assertEqual(c['reported_endpoint'],'seedling growth');self.assertFalse(c['functional_fertility_verified']);self.assertIsNone(c['event_date'])
 def test_idempotent_import_retrieval_and_unresolved_identities(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'test.sqlite3';app.initialize(path);app.initialize(path)
   with app.connect(path) as db:
    c=dict(db.execute("SELECT * FROM crosses WHERE id='happiestplants-bluepap-bvep-dorito'").fetchone())
    self.assertEqual(c['maternal_label'],'Blue Pap');self.assertEqual(c['paternal_label'],'(BVEP × Dorito Portillae)');self.assertEqual(c['direction_known'],1)
    self.assertIsNone(c['maternal_id']);self.assertIsNone(c['paternal_id']);self.assertEqual(c['graph_eligible'],0);self.assertEqual(c['identity_qualified'],0)
    self.assertEqual(db.execute('SELECT accessed FROM sources WHERE id=?',(c['id'],)).fetchone()[0],'2026-11-17')
    self.assertEqual(db.execute('SELECT count(*) FROM evidence_claims WHERE subject_id=?',(c['id'],)).fetchone()[0],1)
    self.assertEqual(db.execute('SELECT count(*) FROM cross_report_sources WHERE cross_id=?',(c['id'],)).fetchone()[0],1)
    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
