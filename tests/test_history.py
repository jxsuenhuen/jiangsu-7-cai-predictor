import unittest,csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from update_history import official_rows,Rows,ROOT
class HistoryTests(unittest.TestCase):
    def test_snapshot(self):
        rows=list(csv.DictReader((ROOT/'history.csv').open(encoding='utf-8-sig')))
        self.assertEqual(len(rows),len({r['issue'] for r in rows}))
        self.assertEqual(rows,sorted(rows,key=lambda r:int(r['issue'])))
        self.assertTrue(all(len(r['issue'])==5 and all(r[f'd{i}'] in '0123456789' and len(r[f'd{i}'])==1 for i in range(1,8)) for r in rows))
        meta=json.loads((ROOT/'data-status.json').read_text())
        self.assertEqual(meta['official_count'],sum(r['source']=='official' for r in rows))
        self.assertEqual(rows[-1]['issue'],meta['official_last'])
    def test_reject_invalid_download(self):
        for text in ['<html>error</html>','"26170","10","0","0","0","0","0","0"','26170,0,0,0,0,0,0,0']:
            with self.assertRaises(ValueError): official_rows(text)
    def test_html_parser(self):
        p=Rows();p.feed('<tr><td>2026-11-06</td><td>26170</td><td>0 <b>3</b> 1 1 4 7 0</td></tr>')
        self.assertEqual(p.rows,[['2026-11-06','26170','0 3 1 1 4 7 0']])
if __name__=='__main__':unittest.main()
