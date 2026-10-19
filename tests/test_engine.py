import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from engine import FIELDS, evaluate, generate, run
C={'demo_markup_min':.03,'demo_markup_max':.15}
def good():return dict(zip(FIELDS,['A','2025-01-01','US Seller','UK Buyer','US','GB','services','USD','110','100','AGR']))
class Tests(unittest.TestCase):
 def test_clean(self):self.assertEqual(evaluate([good()],C)[0][0]['status'],'no_flags')
 def test_duplicates(self):self.assertEqual([x['status'] for x in evaluate([good(),good()],C)[0]],['quarantined']*2)
 def test_invalid_amounts(self):
  for v in ['NaN','Infinity','abc','','0','-2']:
   r=good();r['cost']=v;a,_=evaluate([r],C);self.assertEqual(a[0]['status'],'quarantined');self.assertEqual(a[0]['markup'],'')
 def test_bad_date(self):
  r=good();r['invoice_date']='2025-02-30';self.assertEqual(evaluate([r],C)[0][0]['status'],'quarantined')
 def test_boundaries(self):
  for v in ['103','115']:
   r=good();r['revenue']=v;self.assertFalse(evaluate([r],C)[1])
 def test_exception(self):
  r=good();r['revenue']='116';self.assertEqual(evaluate([r],C)[1][0]['code'],'DEMO_MARKUP_EXCEPTION')
 def test_currency(self):
  r=good();r['currency']='EUR';a,_=evaluate([r],C);self.assertEqual(a[0]['status'],'out_of_scope');self.assertEqual(a[0]['markup'],'')
 def test_empty(self):self.assertEqual(evaluate([],C),([],[]))
 def test_repeat_run(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);generate(p/'input.csv');(p/'c.json').write_text(json.dumps(C))
   a=run(p/'input.csv',p/'out',p/'c.json');b=run(p/'input.csv',p/'out',p/'c.json')
   self.assertEqual(a['input_sha256'],b['input_sha256']);self.assertEqual(a['statuses'],{'review':2,'quarantined':7,'out_of_scope':1,'no_flags':990})
   with sqlite3.connect(p/'out/review.sqlite') as db:
    self.assertEqual(db.execute('select count(*) from raw_transactions').fetchone()[0],1000)
    self.assertEqual(db.execute('select count(*) from findings f left join raw_transactions r using(row_number) where r.row_number is null').fetchone()[0],0)
 def test_bad_schema(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'bad.csv').write_text('wrong\nvalue\n');(p/'c.json').write_text(json.dumps(C))
   with self.assertRaises(ValueError):run(p/'bad.csv',p/'out',p/'c.json')
