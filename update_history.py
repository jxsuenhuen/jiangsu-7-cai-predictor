import csv
import re
import urllib.request
import os
from html.parser import HTMLParser

OUT = "history.csv"

URL = "https://www.js-lottery.com/wfzq/seven"


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text=[]

    def handle_data(self,data):
        t=data.strip()
        if t:
            self.text.append(t)


def fetch(url):
    req=urllib.request.Request(
        url,
        headers={
            "User-Agent":"Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(req,timeout=30) as r:
        return r.read().decode("utf-8","ignore")


def get_latest():

    html=fetch(URL)

    p=Parser()
    p.feed(html)

    txt=" ".join(p.text)

    # 找期号
    issue=re.search(r'26\d{3}',txt)

    if not issue:
        raise RuntimeError("没有找到最新期号")

    issue=issue.group()

    # 找7个数字
    nums=re.findall(r'(?<!\d)[0-9](?!\d)',txt)

    if len(nums)<7:
        raise RuntimeError("没有找到7位开奖号码")

    nums=nums[-7:]

    return [
        issue,
        "2026-10-12",
        *map(int,nums)
    ]


def read():

    if not os.path.exists(OUT):
        return []

    with open(
        OUT,
        encoding="utf-8-sig",
        newline=""
    ) as f:

        return list(csv.reader(f))[1:]


def write(rows):

    rows=sorted(
        rows,
        key=lambda x:int(x[0])
    )

    with open(
        OUT,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        w=csv.writer(f)

        w.writerow(
            [
                "issue",
                "date",
                "d1",
                "d2",
                "d3",
                "d4",
                "d5",
                "d6",
                "d7"
            ]
        )

        w.writerows(rows)


def main():

    rows=read()

    latest=get_latest()

    exist=False

    for r in rows:
        if r[0]==latest[0]:
            exist=True

    if not exist:
        rows.append(
            list(map(str,latest))
        )

        print(
            "新增:",
            latest
        )

    else:
        print(
            "已有:",
            latest[0]
        )

    write(rows)


if __name__=="__main__":
    main()
