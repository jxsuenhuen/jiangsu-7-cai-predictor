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
        self.data = []

    def handle_data(self, data):
        t = data.strip()
        if t:
            self.data.append(t)


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")

def get_history():

    url = "https://api.huiniao.top/interface/home/lotteryHistory"

    req = urllib.request.Request(
        url + "?type=jsqws&page=1&limit=500",
        headers={
            "User-Agent":"Mozilla/5.0"
        }
    )

    import json

    with urllib.request.urlopen(req,timeout=30) as r:
        obj=json.loads(
            r.read().decode("utf-8-sig")
        )

    rows=[]

    data=obj["data"]["data"]["list"]

    for x in data:

        issue=str(x.get("code",""))

        nums=[
            x.get("one"),
            x.get("two"),
            x.get("three"),
            x.get("four"),
            x.get("five"),
            x.get("six"),
            x.get("seven")
        ]

        date=x.get("day","")

        if (
            re.fullmatch(r"\d{5}",issue)
            and len(nums)==7
        ):
            rows.append([
                issue,
                date,
                *nums
            ])

    return rows
def get_latest():

    html = fetch(URL)

    p = Parser()
    p.feed(html)

    text = "\n".join(p.data)

    # 只寻找开奖公告格式：
    # 26155
    # 开奖号码
    # 1 1 1 7 2 5 2

    match = re.search(
        r'(261\d{2}).{0,200}?'
        r'([0-9])\s+([0-9])\s+([0-9])\s+'
        r'([0-9])\s+([0-9])\s+([0-9])\s+([0-9])',
        text,
        re.S
    )

    if not match:
        raise RuntimeError("未找到有效7位数开奖")

    issue = match.group(1)

    nums = [
        int(match.group(i))
        for i in range(2,9)
    ]

    # 防止抓错期号
    if not issue.startswith("261"):
        raise RuntimeError(
            f"错误期号:{issue}"
        )

    return [
        issue,
        "2026-10-12",
        *nums
    ]


def read_history():

    if not os.path.exists(OUT):
        return []

    with open(
        OUT,
        encoding="utf-8-sig",
        newline=""
    ) as f:

        return list(csv.reader(f))[1:]


def save(rows):

    rows = sorted(
        rows,
        key=lambda x:int(x[0])
    )

    with open(
        OUT,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        w = csv.writer(f)

        w.writerow([
            "issue",
            "date",
            "d1",
            "d2",
            "d3",
            "d4",
            "d5",
            "d6",
            "d7"
        ])

        w.writerows(rows)


def main():

    rows = read_history()


# 第一次运行，初始化历史
if len(rows)<100:

    print("开始下载历史数据")

    rows=get_history()

    print(
        "历史数量:",
        len(rows)
    )


latest=get_latest()

     

    exists = False

    for r in rows:
        if r[0] == latest[0]:
            exists = True

    if not exists:

        rows.append(
            list(map(str, latest))
        )

        print(
            "新增:",
            latest
        )

    else:

        print(
            "已有:",
            latest
        )


    save(rows)

    print(
        "完成，最新期:",
        latest[0]
    )


if __name__ == "__main__":
    main()
