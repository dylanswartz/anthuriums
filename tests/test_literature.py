import json,tempfile,unittest
from pathlib import Path
import app
class LiteratureTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'literature.sqlite3';app.initialize(self.path);self.db=app.connect(self.path)
  self.d=json.loads((app.ROOT/'research/published_open_pollination.json').read_text());self.c=dict(self.db.execute('SELECT * FROM crosses WHERE id=?',(self.d['id'],)).fetchone())
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def test_spelling_alignment_is_not_a_new_taxonomic_synonym(self):
  self.assertEqual(self.db.execute('SELECT name FROM species WHERE id=?',(self.c['paternal_id'],)).fetchone()[0],'Anthurium wendlingeri')
  self.assertEqual(self.d['original_spelling'],'Anthurium wendlingerii')
  self.assertIn('not added as a verified nomenclatural synonym',self.d['spelling_alignment'])
 def test_open_pollination_does_not_confirm_father_or_fertility(self):
  self.assertEqual(self.c['direction_known'],0);self.assertEqual(self.c['identity_qualified'],0);self.assertEqual(self.c['graph_eligible'],0)
  self.assertFalse(self.d['functional_fertility_verified']);self.assertIn('not controlled or genetically confirmed',self.c['uncertainty'])
  self.assertEqual(self.c['access_level'],'primary-source search index/abstract, full text not inspected')
  self.assertEqual(self.db.execute('SELECT count(*) FROM fertility_assertions').fetchone()[0],0)
 def test_linked_publications_remain_one_report_on_reinitialization(self):
  app.initialize(self.path)
  self.assertEqual(self.db.execute('SELECT count(*) FROM crosses WHERE report_family_id=?',(self.d['report_family_id'],)).fetchone()[0],1)
  self.assertEqual(self.db.execute('SELECT count(*) FROM cross_report_sources WHERE cross_id=?',(self.d['id'],)).fetchone()[0],2)
  self.assertEqual(self.db.execute('SELECT count(*) FROM evidence_claims WHERE subject_id=?',(self.d['id'],)).fetchone()[0],2)
  self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(),[])
  self.assertEqual(len([s for s in app.dataset(self.db)['cross_report_sources'] if s['cross_id']==self.d['id']]),2)
