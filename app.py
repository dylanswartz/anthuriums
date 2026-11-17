"""Anthurium Atlas: local, single-user botanical research notebook. No third-party dependencies."""
import argparse, datetime, hashlib, json, os, sqlite3
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('ANTHURIUM_ATLAS_DB', ROOT / 'data/anthurium-atlas.sqlite3'))
TABLES = ['sources','sections','species','taxonomic_records','crosses']
STAGES = ['pollination','fruit set','seed harvested','germination','seedling survival','flowering','fertility assessed','no observed result']
def connect(path=None):
    db = sqlite3.connect(path or DB)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db

def import_seed(db, payload):
    if set(payload) != set(TABLES): raise ValueError('Seed requires exactly: '+', '.join(TABLES))
    with db:
        for table in TABLES:
            allowed = {r['name'] for r in db.execute('PRAGMA table_info('+table+')')}
            for row in payload[table]:
                if not isinstance(row,dict) or not row or set(row)-allowed: raise ValueError('Invalid columns in '+table)
                if table=='sources' and not row.get('url','').startswith('https://'): raise ValueError('Citations require HTTPS URLs')
                cols=list(row)
                updates=','.join(c+'=excluded.'+c for c in cols if c!='id')
                sql='INSERT INTO '+table+' ('+','.join(cols)+') VALUES ('+','.join('?' for _ in cols)+') ON CONFLICT(id) DO UPDATE SET '+updates
                db.execute(sql,[row[c] for c in cols])
        db.execute("INSERT OR REPLACE INTO metadata VALUES ('seed_version','1')")

def initialize(path=None):
    target=Path(path or DB); target.parent.mkdir(parents=True, exist_ok=True)
    db=connect(target); db.executescript((ROOT/'schema.sql').read_text())
    from research_db import migrate, ingest_research, ingest_labels, ingest_literature, ingest_grower_additions
    migrate(db)
    seed=(ROOT/'data/seed.json').read_bytes();digest=hashlib.sha256(seed).hexdigest()
    previous=db.execute('SELECT value FROM metadata WHERE key=?',('seed_checksum',)).fetchone()
    if not previous or previous[0]!=digest:
        import_seed(db,json.loads(seed))
        with db:db.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('seed_checksum',digest))
    ingest_research(db); ingest_labels(db); ingest_literature(db); ingest_grower_additions(db)
    db.close()

def dataset(db):
    return {t:[dict(r) for r in db.execute('SELECT * FROM '+t)] for t in TABLES+['observations','label_assertions','cross_report_sources']}

def add_observation(db, p):
    required={'maternal_id','paternal_id','observed_on','stage','notes'}
    if not isinstance(p,dict) or set(p)!=required: raise ValueError('Provide parents, date, stage, and notes')
    if not all(isinstance(v,str) for v in p.values()): raise ValueError('All fields must be text')
    if p['stage'] not in STAGES: raise ValueError('Unknown observation stage')
    try: date=datetime.date.fromisoformat(p['observed_on'])
    except ValueError: raise ValueError('Use a valid observation date')
    if date>datetime.date.today(): raise ValueError('Observation date cannot be in the future')
    if not p['notes'].strip() or len(p['notes'])>5000: raise ValueError('Notes must contain 1–5000 characters')
    for key in ['maternal_id','paternal_id']:
        if not db.execute('SELECT 1 FROM species WHERE id=?',(p[key],)).fetchone(): raise ValueError('Choose an existing species for both parents')
    with db:
        cur=db.execute('INSERT INTO observations(maternal_id,paternal_id,observed_on,stage,notes) VALUES (?,?,?,?,?)',tuple(p[k] for k in ['maternal_id','paternal_id','observed_on','stage','notes']))
    return dict(db.execute('SELECT * FROM observations WHERE id=?',(cur.lastrowid,)).fetchone())

class Handler(BaseHTTPRequestHandler):
    def respond(self,status,value,kind='application/json; charset=utf-8'):
        body=json.dumps(value,ensure_ascii=False).encode() if kind.startswith('application/json') else value
        self.send_response(status); self.send_header('Content-Type',kind); self.send_header('Content-Length',str(len(body)))
        self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Cache-Control','no-store')
        self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ['/api/data','/api/export']:
            with connect() as db:
                result=dataset(db)
                if path=='/api/export':
                    from research_db import RESEARCH_TABLES
                    result['research']={t:[dict(r) for r in db.execute('SELECT * FROM '+t)] for t in RESEARCH_TABLES}
                self.respond(200,result)
        elif path=='/api/research':
            from research_db import RESEARCH_TABLES
            with connect() as db: self.respond(200,{t:[dict(r) for r in db.execute('SELECT * FROM '+t)] for t in RESEARCH_TABLES if t not in ['taxon_names','taxonomic_assertions','evidence_claims']})
        elif path in ['/','/app.js','/style.css']:
            file={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[path]
            self.respond(200,(ROOT/'static'/file).read_bytes(),{'index.html':'text/html; charset=utf-8','app.js':'text/javascript; charset=utf-8','style.css':'text/css; charset=utf-8'}[file])
        else: self.respond(404,{'error':'Not found'})
    def do_POST(self):
        self.respond(405,{'error':'This explorer is read-only. Recording UI is not enabled.'})

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--strictPort',action='store_true'); parser.add_argument('--host',default='127.0.0.1'); parser.add_argument('--port',type=int,default=8000); args=parser.parse_args()
    initialize(); print(f'Anthurium Atlas · http://{args.host}:{args.port}',flush=True)
    ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()
