"""Synchronize the complete official download; retain older legacy rows with provenance."""
import csv, io, json, re, time, os
from pathlib import Path
from urllib.request import Request, urlopen
from html.parser import HTMLParser
from datetime import date, datetime, timezone
ROOT=Path(__file__).resolve().parent
DOWNLOAD='https://api.js-lottery.com/lottery/downSevenData'
PAGE='https://api.js-lottery.com/wfzq/seven/data'

def fetch(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as r:
                return r.read().decode('utf-8-sig')
        except Exception:
            if attempt==2: raise
            time.sleep(2**attempt)

class Rows(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows=[]; self.row=[]; self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr': self.row=[]
        if tag=='td': self.cell=''
    def handle_data(self,data):
        if self.cell is not None: self.cell+=data
    def handle_endtag(self,tag):
        if tag=='td' and self.cell is not None:
            self.row.append(' '.join(self.cell.split())); self.cell=None
        if tag=='tr' and self.row: self.rows.append(self.row)

def official_rows(text):
    result={}
    for row in csv.reader(io.StringIO(text)):
        if not row: continue
        if len(row)!=8 or not re.fullmatch(r'\d{5}',row[0]) or any(not re.fullmatch('[0-9]',v) for v in row[1:]):
            raise ValueError('Invalid official download row')
        if row[0] in result: raise ValueError('Duplicate official issue')
        result[row[0]]=row[1:]
    if len(result)<4000: raise ValueError('Official history unexpectedly truncated')
    return result

def main():
    # Optional local snapshots are for repeatable verification only.
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--download'); p.add_argument('--page'); args=p.parse_args()
    official=official_rows(Path(args.download).read_text() if args.download else fetch(DOWNLOAD))
    parser=Rows(); parser.feed(Path(args.page).read_text() if args.page else fetch(PAGE))
    dates={}
    for row in parser.rows:
        if len(row)>=3 and re.fullmatch(r'\d{4}-\d{2}-\d{2}',row[0]) and re.fullmatch(r'\d{5}',row[1]):
            digits=row[2].split()
            if len(digits)!=7 or any(not re.fullmatch('[0-9]',v) for v in digits): raise ValueError('Bad official detail row')
            date.fromisoformat(row[0]); dates[row[1]]=row[0]
            if row[1] in official and official[row[1]]!=digits: raise ValueError('Official sources disagree; retry later')
            official[row[1]]=digits
    if not dates: raise ValueError('No official dates parsed')
    path=ROOT/'history.csv'
    old={r['issue']:r for r in csv.DictReader(path.open(encoding='utf-8-sig'))} if path.exists() else {}
    previously_verified={k for k,v in old.items() if v.get('source')=='official'}
    if not previously_verified.issubset(official): raise ValueError('Official source lost previously verified records')
    changes=[]
    for issue,digits in official.items():
        previous=old.get(issue,{})
        if previous and digits!=[previous['d'+str(i)] for i in range(1,8)]: changes.append(issue)
        old[issue]={'issue':issue,'date':dates.get(issue,previous.get('date','')),
                    **{'d'+str(i):v for i,v in enumerate(digits,1)},'source':'official',
                    'date_source':'official' if issue in dates or previous.get('date_source')=='official' else 'legacy'}
    rows=sorted(old.values(),key=lambda r:int(r['issue']))
    fields=['issue','date',*[f'd{i}' for i in range(1,8)],'source','date_source']
    for r in rows:
        r.setdefault('source','legacy'); r.setdefault('date_source','legacy')
    tmp=path.with_suffix('.tmp')
    with tmp.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    os.replace(tmp,path)
    metadata={'checked_at':datetime.now(timezone.utc).isoformat(),'official_count':len(official),
      'official_first':min(official,key=int),'official_last':max(official,key=int),
      'legacy_count':len(rows)-len(official),'download_url':DOWNLOAD,'page_url':PAGE,
      'note':'官方号码下载不含日期；较早日期沿用旧版，未逐期核验。早于官方下载范围的记录保留并标为旧版来源。'}
    (ROOT/'data-status.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'total':len(rows),'official':len(official),'corrected':changes},ensure_ascii=False))
if __name__=='__main__': main()
