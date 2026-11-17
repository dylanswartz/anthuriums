import json,tempfile,unittest
from pathlib import Path
import app
class RochaniTests(unittest.TestCase):
 def test_source_roles_accession_and_unknown_outcomes(self):
  c=json.loads((app.ROOT/'research/rochani_registration.json').read_text())['records'][0]
  self.assertEqual(c['maternal_accession_label'],'GCI 002');self.assertEqual(c['registration_id'],'1028/PVHP/2023');self.assertEqual(c['registration_date'],'2023-05-31');self.assertEqual(c['publication_id'],'140/BR/PVHP/05/2023')
  self.assertIn('28–29',c['citation_detail']);self.assertEqual(c['reported_endpoint'],'flowering');self.assertFalse(c['functional_fertility_verified'])
  for k in ['event_date','germination_rate','fertility','reciprocal_outcome']:self.assertIsNone(c[k])
 def test_idempotent_registry_claim_preserves_qualified_species_mapping(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'db.sqlite3';app.initialize(path);app.initialize(path)
   with app.connect(path) as db:
    c=dict(db.execute("SELECT * FROM crosses WHERE id='indonesia-rochani-2023'").fetchone())
    self.assertEqual(c['maternal_label'],'Anthurium veitchii GCI 002');self.assertEqual(c['direction_known'],1)
    for role,name in [('maternal','Anthurium veitchii'),('paternal','Anthurium forgetii')]:self.assertEqual(db.execute('SELECT name FROM species WHERE id=?',(c[role+'_id'],)).fetchone()[0],name)
    self.assertEqual(c['graph_eligible'],1);self.assertIn('not DNA confirmation',c['uncertainty'])
    claims=db.execute('SELECT evidence_type,locator FROM evidence_claims WHERE subject_id=?',(c['id'],)).fetchall();self.assertEqual(len(claims),1);self.assertEqual(claims[0][0],'registrar-record');self.assertIn('1028/PVHP/2023',claims[0][1])
    self.assertEqual(db.execute('SELECT accessed FROM sources WHERE id=?',(c['id'],)).fetchone()[0],'2026-11-17');self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
