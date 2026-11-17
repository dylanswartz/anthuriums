#!/usr/bin/env python3
"""Review and apply a local normalized seed. This command never fetches URLs."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app
p=argparse.ArgumentParser(description=__doc__);p.add_argument('file',type=Path);p.add_argument('--apply',action='store_true');args=p.parse_args()
payload=json.loads(args.file.read_text());app.initialize()
# Validate everything transactionally in an isolated in-memory copy first.
with app.connect() as live:
 import sqlite3
 trial=sqlite3.connect(':memory:');trial.row_factory=sqlite3.Row;trial.execute('PRAGMA foreign_keys=ON');live.backup(trial)
 app.import_seed(trial,payload)
 for table in app.TABLES:
  before={r['id']:dict(r) for r in live.execute('SELECT * FROM '+table)}
  after={r['id']:dict(r) for r in trial.execute('SELECT * FROM '+table)}
  added=set(after)-set(before);changed=[k for k in before if k in after and before[k]!=after[k]]
  print(f'{table}: {len(added)} additions; {len(changed)} changed; 0 removals (merge-only)')
 if args.apply:
  backup=app.DB.with_suffix('.preimport.sqlite3')
  with sqlite3.connect(backup) as dest:live.backup(dest)
  app.import_seed(live,payload);print('Applied. Backup:',backup)
 else:print('Review only. Repeat with --apply after reviewing source terms and facts.')
