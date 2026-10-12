import csv,json,urllib.parse,urllib.request,re,time,os
from html.parser import HTMLParser

OFFICIAL='https://api.js-lottery.com/wfzq/seven/data'
FALLBACK='https://api.huiniao.top/interface/home/lotteryHistory'
OUT='history.csv'; LIMIT=500

class TableParser(HTMLParser):
    def __init__(self): super().__init__(); self.in_td=False; self.buf=[]; self.cells=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('td','th'): self.in_td=True; self.buf=[]
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.in_td:
            self.cells.append(' '.join(''.join(self.buf).split())); self.in_td=False
    def handle_data(self,data):
        if self.in_td: self.buf.append(data)

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Cache-Control':'no-cache'})
    with urllib.request.urlopen(req,timeout=30) as r: return r.read().decode('utf-8','replace')

def official_latest():
    html=fetch(OFFICIAL+'?t='+str(int(time.time())))
    p=TableParser(); p.feed(html)
    rows=[]
    c=p.cells
    for i in range(len(c)-8):
        date,issue=c[i],c[i+1]
        nums=c[i+2:i+9]
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}',date) and re.fullmatch(r'\d{5}',issue) and all(re.fullmatch(r'\d',x) for x in nums):
            rows.append([issue,date,*map(int,nums)])
    if not rows: raise RuntimeError('官方江苏体彩网历史数据页面未解析到有效7位数记录')
    rows.sort(key=lambda r:int(r[0]))
    return rows[-1]

def fallback_full():
    url = FALLBACK + '?' + urllib.parse.urlencode({
        'type': 'jsqws',
        'page': 1,
        'limit': LIMIT
    })

    req = urllib.request.Request(
        url,
        headers={'User-Agent':'Mozilla/5.0'}
    )

    with urllib.request.urlopen(req, timeout=30) as r:
        obj = json.loads(r.read().decode('utf-8-sig','replace'))

    rows=[]

    data = obj.get('data',{})

    items = []

    if isinstance(data, dict):
        if 'list' in data:
            items=data['list']
        elif isinstance(data.get('data'),dict):
            items=data['data'].get('list',[])

    for x in items:
        code=str(x.get('code',''))
        day=str(x.get('day',''))

        nums=[
            x.get('one'),
            x.get('two'),
            x.get('three'),
            x.get('four'),
            x.get('five'),
            x.get('six'),
            x.get('seven')
        ]

        if (
            re.fullmatch(r'\d{5}',code)
            and all(
                v is not None 
                and str(v).isdigit()
                and 0<=int(v)<=9
                for v in nums
            )
        ):
            rows.append([
                code,
                day,
                *map(int,nums)
            ])

    rows.sort(key=lambda r:int(r[0]))

    if not rows:
        raise RuntimeError('备用接口没有返回7位数数据')

    return rows

def write(rows):
    rows=sorted({r[0]:r for r in rows}.values(),key=lambda r:int(r[0]))
    with open(OUT,'w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f); w.writerow(['issue','date','d1','d2','d3','d4','d5','d6','d7']); w.writerows(rows)
    print(f'OK {len(rows)} rows; latest={rows[-1][0]} {rows[-1][1]} {"".join(map(str,rows[-1][2:]))}')

def main():
    rows=read_rows()

    if len(rows)<4748:
       rows=fallback_full()
        print('Seeded full history from fallback source.')

    # 使用备用接口获取最新数据
    latest_rows=fallback_full()
    latest=latest_rows[-1]

    if not rows or int(latest[0])>int(rows[-1][0]):
        rows.append(latest)
        print('Latest appended:', latest)

    elif int(latest[0])==int(rows[-1][0]):
        print('Already latest:', latest)

    write(rows)
