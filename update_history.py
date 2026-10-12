import csv
import os
import re
import time
import urllib.request
from html.parser import HTMLParser


OUT = "history.csv"

URL = "https://www.js-lottery.com/wfzq/seven"


class Parser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        t = data.strip()
        if t:
            self.text.append(t)


def fetch(url):

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent":
            "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(
        req,
        timeout=30
    ) as r:

        return r.read().decode(
            "utf-8",
            "ignore"
        )



def parse_page(html):

    p = Parser()
    p.feed(html)

    text = "\n".join(p.text)


    result = []


    # 查找期号+7位号码

    pattern = re.compile(
        r'(\d{5}).{0,300}?'
        r'([0-9])\s+'
        r'([0-9])\s+'
        r'([0-9])\s+'
        r'([0-9])\s+'
        r'([0-9])\s+'
        r'([0-9])\s+'
        r'([0-9])',
        re.S
    )


    for m in pattern.findall(text):

        issue = m[0]

        nums = list(
            map(int,m[1:])
        )


        if issue.startswith("26"):

            result.append(
                [
                    issue,
                    "",
                    *nums
                ]
            )


    return result



def get_all_history():

    print(
        "开始抓取历史数据..."
    )


    html = fetch(
        URL + "?t=" + str(int(time.time()))
    )


    rows = parse_page(html)


    if len(rows)<10:

        raise RuntimeError(
            "历史数据解析失败"
        )


    return rows



def get_latest():

    rows = get_all_history()

    rows.sort(
        key=lambda x:int(x[0])
    )

    return rows[-1]



def read_csv():

    if not os.path.exists(OUT):

        return []


    with open(
        OUT,
        encoding="utf-8-sig",
        newline=""
    ) as f:


        data=list(
            csv.reader(f)
        )


    return data[1:]



def save(rows):

    rows.sort(
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


    old = read_csv()



    # 第一次运行

    if len(old)<100:


        print(
            "历史不足，重新初始化"
        )


        rows=get_all_history()


    else:


        print(
            "已有历史，只更新最新"
        )


        rows=old


        latest=get_latest()


        exists=False


        for r in rows:

            if r[0]==latest[0]:

                exists=True



        if not exists:

            rows.append(
                latest
            )

            print(
                "新增:",
                latest
            )



    # 去重

    result={}


    for r in rows:

        result[r[0]]=r



    rows=list(
        result.values()
    )


    save(rows)


    print(
        "完成"
    )

    print(
        "总期数:",
        len(rows)
    )

    print(
        "最新:",
        rows[-1]
    )



if __name__=="__main__":

    main()
