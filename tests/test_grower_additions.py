import tempfile,unittest
from pathlib import Path
import app
class GrowerAdditionTests(unittest.TestCase):
 def test_roles_compound_identity_and_idempotent_provenance(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'test.sqlite3';app.initialize(path);app.initialize(path)
   with app.connect(path) as db:
    l=dict(db.execute("SELECT * FROM crosses WHERE id='lutz-forgetii-clarinervium-2024'").fetchone())
    self.assertEqual(l['maternal_label'],'Anthurium forgetii');self.assertEqual(l['paternal_label'],'Anthurium clarinervium');self.assertEqual(l['direction_known'],1)
    self.assertIn('title reverses',l['uncertainty']);self.assertIn('Suspected/unconfirmed',l['uncertainty']);self.assertEqual(l['graph_eligible'],0);self.assertEqual(l['identity_qualified'],0)
    c=dict(db.execute("SELECT * FROM crosses WHERE id='steves-crystallinum-magnificum-clarinervium'").fetchone())
    self.assertIsNone(c['maternal_id']);self.assertEqual(c['maternal_label'],'Anthurium (crystallinum × magnificum)');self.assertEqual(c['direction_known'],0);self.assertEqual(c['graph_eligible'],0)
    self.assertEqual(db.execute('SELECT name FROM species WHERE id=?',(c['paternal_id'],)).fetchone()[0],'Anthurium clarinervium')
    self.assertTrue(db.execute('SELECT url FROM sources WHERE id=?',(c['id'],)).fetchone()[0].endswith('clarinervum'))
    for x in [l,c]:
     self.assertEqual(x['reported_endpoint'],'seedling growth');self.assertIn('inspected',x['access_level']);self.assertEqual(db.execute('SELECT count(*) FROM evidence_claims WHERE subject_id=?',(x['id'],)).fetchone()[0],1)
     self.assertEqual(db.execute('SELECT count(*) FROM cross_report_sources WHERE cross_id=?',(x['id'],)).fetchone()[0],1)
    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
