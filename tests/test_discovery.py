import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from scripts.discover_names import candidates,discover,extract_names,public_https,resolve_name,stage
import app
class DiscoveryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.snapshot=json.loads((app.ROOT/'research/wcvp_anthurium_v16.json').read_text())
 def test_disabled_means_zero_requests(self):
  with patch('scripts.discover_names.fetch',side_effect=AssertionError('network should not run')):
   rows,log=discover({'enabled':False});self.assertEqual(rows,[]);self.assertIn('disabled',log['status'])
 def test_exact_names_do_not_authenticate_trade_labels(self):
  match=resolve_name('Anthurium crystallinum',self.snapshot['records']);self.assertEqual(match['accepted_name'],'Anthurium crystallinum');self.assertFalse(match['identity_verified'])
  self.assertIsNone(resolve_name('Blue Pap',self.snapshot['records'])['accepted_id'])
  self.assertIsNone(resolve_name('Anthurium forgetti',self.snapshot['records'])['accepted_id'])
 def test_html_extracts_only_names_not_scripts_or_prose(self):
  names=extract_names('<p>Find Anthurium crystallinum today.</p><script>Anthurium invented</script><img src="private.png">','html_names');self.assertEqual(names,['Anthurium crystallinum'])
 def test_all_permissions_validated_before_requests(self):
  config={'enabled':True,'sources':[{'id':'bad','url':'https://example.org/names','terms_url':'https://example.org/terms','terms_reviewed':False,'format':'json_names'}]}
  with patch('scripts.discover_names.fetch',side_effect=AssertionError('no network')):
   with self.assertRaises(ValueError):discover(config)
 def test_nonpublic_targets_rejected(self):
  for url in ['http://example.org','https://127.0.0.1','https://localhost','https://user:pass@example.org']:
   with self.assertRaises(ValueError):public_https(url)
 def test_provenance_pending_no_popularity_or_promotion(self):
  rows=[{'name':'Anthurium crystallinum','source_url':'https://example.org/names','observed_on':'2026-01-01'}]
  result=candidates(rows+rows,self.snapshot);self.assertEqual(len(result),1);self.assertEqual(result[0]['review_status'],'pending');self.assertIsNone(result[0]['popularity']);self.assertFalse(result[0]['cross_evidence_promoted'])
  with tempfile.TemporaryDirectory() as directory:
   path,count=stage(rows,{'status':'synthetic test'},directory);self.assertEqual(count,1);self.assertTrue(Path(path).is_file());self.assertEqual(json.loads(path.read_text())['candidates'][0]['source_url'],'https://example.org/names')
 def source(self,url,**extra):
  return {'id':url,'url':url,'terms_url':'https://example.org/terms','terms_reviewed':True,'permission_note':'Synthetic test permission','format':'json_names',**extra}
 def test_granthuriums_automation_denied_before_any_network(self):
  for host in ['granthuriums.com','www.granthuriums.com','shop.granthuriums.com','nsetropicals.com','www.nsetropicals.com','carnivero.com','shop.carnivero.com']:
   with patch('scripts.discover_names.fetch',side_effect=AssertionError('no network')):
    with self.assertRaisesRegex(ValueError,'prohibited'):
     discover({'enabled':True,'sources':[self.source('https://example.org/allowed'),self.source('https://'+host+'/plants')]})
  result=candidates([{'name':'Trade label','source_url':'https://granthuriums.com/products/example','observed_on':'2026-01-01'}],self.snapshot)
  self.assertEqual(len(result),1)
 def test_request_pacing_and_robots_cached_per_origin(self):
  clock=[0.0];calls=[]
  def sleep(seconds):clock[0]+=seconds
  def response(url,limit):
   calls.append((url,clock[0]))
   return b'User-agent: *\nAllow: /\nCrawl-delay: 2.5\nRequest-rate: 1/8' if url.endswith('/robots.txt') else b'{"names":["Anthurium crystallinum"]}'
  with patch('scripts.discover_names.time.monotonic',side_effect=lambda:clock[0]),patch('scripts.discover_names.time.sleep',side_effect=sleep),patch('scripts.discover_names.fetch',side_effect=response):
   rows,log=discover({'enabled':True,'min_interval_seconds':3,'sources':[self.source('https://example.org/a'),self.source('https://example.org/b',min_interval_seconds=12)]})
  self.assertEqual([t for _,t in calls],[0,8,20]);self.assertEqual(len(rows),2)
  self.assertEqual(log['sources'][0]['effective_min_interval_seconds'],8)
  self.assertEqual(log['sources'][1]['effective_min_interval_seconds'],12)
 def test_robots_disallow_and_invalid_timing_fail_closed(self):
  for body in [b'User-agent: *\nDisallow: /',b'User-agent: *\nCrawl-delay: nonsense',b'User-agent: *\nRequest-rate: 0/5']:
   with patch('scripts.discover_names.fetch',return_value=body) as fetch:
    with self.assertRaises(ValueError):discover({'enabled':True,'sources':[self.source('https://example.org/a')]})
    self.assertEqual(fetch.call_count,1)
 def test_invalid_configured_interval_rejected_before_requests(self):
  for value in [0,-1,True,float('nan'),'5']:
   with patch('scripts.discover_names.fetch',side_effect=AssertionError('no network')):
    with self.assertRaises(ValueError):discover({'enabled':True,'min_interval_seconds':value,'sources':[self.source('https://example.org/a')]})
if __name__=='__main__':unittest.main()
