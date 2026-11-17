#!/usr/bin/env python3
"""Accession-level CLI; JSON input keeps scientific observations explicit."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app,research_db
p=argparse.ArgumentParser();p.add_argument('operation',choices=['accession','plan','attempt','outcome','pedigree','export']);p.add_argument('json_or_id',nargs='?',default='{}');a=p.parse_args();app.initialize()
with app.connect() as db:
 if a.operation=='pedigree':result=research_db.pedigree(db,a.json_or_id)
 elif a.operation=='export':result={t:[dict(r) for r in db.execute('SELECT * FROM '+t)] for t in research_db.RESEARCH_TABLES}
 else:
  fn={'accession':research_db.create_accession,'plan':research_db.create_plan,'attempt':research_db.record_attempt,'outcome':research_db.record_outcome}[a.operation]
  fn(db,**json.loads(a.json_or_id));result={'saved':a.operation}
 print(json.dumps(result,indent=2,ensure_ascii=False))
