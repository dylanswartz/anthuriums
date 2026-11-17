import json,tempfile,unittest
from pathlib import Path
import app,research_db
class SellerReportTests(unittest.TestCase):
 def test_existing_database_upgrade_and_distinct_source_claims(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'old.sqlite3'
   with app.connect(path) as db:
    db.executescript((app.ROOT/'schema.sql').read_text());research_db.migrate(db)
    old=json.loads((app.ROOT/'data/seed.json').read_text())
    old['crosses']=[c for c in old['crosses'] if not c['id'].startswith('palmstreet-')];old['sources']=[s for s in old['sources'] if not s['id'].startswith('palmstreet-')]
    app.import_seed(db,old)
   app.initialize(path);app.initialize(path)
   with app.connect(path) as db:
    rows=[dict(c) for c in db.execute("SELECT * FROM crosses WHERE id LIKE 'palmstreet-%' ORDER BY id")]
    self.assertEqual(len(rows),2);self.assertEqual(len({c['report_family_id'] for c in rows}),2)
    self.assertEqual({c['reported_endpoint'] for c in rows},{'germination','newly sprouted seedling'})
    for c in rows:
     self.assertIsNone(c['maternal_id']);self.assertIsNone(c['paternal_id']);self.assertEqual(c['graph_eligible'],0);self.assertEqual(c['identity_qualified'],0)
     self.assertEqual(db.execute('SELECT count(*) FROM evidence_claims WHERE subject_id=?',(c['id'],)).fetchone()[0],1)
     self.assertEqual(db.execute('SELECT count(*) FROM cross_report_sources WHERE cross_id=?',(c['id'],)).fetchone()[0],1)
    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
 def test_seller_parent_origin_and_inspiration_are_separate(self):
  rows=json.loads((app.ROOT/'research/palmstreet_seller_reports.json').read_text())['records'];a,b=rows
  self.assertEqual(a['seller'],'DannyGardner');self.assertEqual(a['parent_origin_attribution']['pollen_parent'],'Justin Jones')
  self.assertEqual(a['maternal_label'],'Besseae aff.');self.assertEqual(a['paternal_label'],"FSRL × BVEP 'Felix'")
  self.assertEqual(b['parent_origin_attribution'],{'seed_parent':'Teo','seed_parent_source':'Yolanda Picklesauce','pollen_parent':'Jay Vannini'})
  self.assertEqual(b['inspiration_mention']['attributed_to'],'Seth Schweers');self.assertIn('not an independently observed event',b['inspiration_mention']['status'])
  for c in rows:self.assertIsNone(c['event_date']);self.assertFalse(c['functional_fertility_verified']);self.assertEqual(c['retrieved'],'2026-11-17')
