import csv
import os
import json
import urllib.request
import urllib.parse


OUT = "history.csv"


API = (
    "https://api.huiniao.top/interface/home/lotteryHistory?"
)


# ==========================
# 获取全部历史
# ==========================

def get_all_history():

    rows = []

    # 先获取第一页
    url = API + urllib.parse.urlencode(
        {
            "type": "jsqws",
            "page": 1,
            "limit": 500
        }
    )


    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )


    with urllib.request.urlopen(
        req,
        timeout=30
    ) as r:

        obj = json.loads(
            r.read().decode(
                "utf-8-sig"
            )
        )


    total_page = int(
        obj["data"]["data"]["totalPage"]
    )


    print(
        "总页数:",
        total_page
    )


    # 分页抓取

    for page in range(
        1,
        total_page + 1
    ):


        print(
            "抓取第",
            page,
            "页"
        )


        url = API + urllib.parse.urlencode(
            {
                "type": "jsqws",
                "page": page,
                "limit": 500
            }
        )


        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )


        with urllib.request.urlopen(
            req,
            timeout=30
        ) as r:


            data = json.loads(
                r.read().decode(
                    "utf-8-sig"
                )
            )


        items = data["data"]["data"]["list"]


        for x in items:


            issue = str(
                x["code"]
            )


            nums = [
                x["one"],
                x["two"],
                x["three"],
                x["four"],
                x["five"],
                x["six"],
                x["seven"]
            ]


            rows.append(
                [
                    issue,
                    x["day"],
                    *map(int, nums)
                ]
            )



    # 排序

    rows.sort(
        key=lambda x:int(x[0])
    )


    print(
        "抓取完成:",
        len(rows),
        "期"
    )


    return rows



# ==========================
# 读取已有CSV
# ==========================

def read_history():


    if not os.path.exists(OUT):

        return []


    with open(
        OUT,
        encoding="utf-8-sig",
        newline=""
    ) as f:


        data = list(
            csv.reader(f)
        )


    return data[1:]



# ==========================
# 保存CSV
# ==========================

def save_history(rows):


    rows.sort(
        key=lambda x:int(x[0])
    )


    with open(
        OUT,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:


        w = csv.writer(f)


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



# ==========================
# 主程序
# ==========================

def main():


    old = read_history()



    # 第一次运行
    if len(old) < 100:


        print(
            "历史不足，重新初始化"
        )


        rows = get_all_history()



    else:


        print(
            "已有历史，只更新"
        )


        all_rows = get_all_history()


        latest = all_rows[-1]


        rows = old


        exists = False


        for r in rows:

            if r[0] == str(latest[0]):

                exists = True



        if not exists:

            rows.append(
                list(
                    map(str, latest)
                )
            )

            print(
                "新增:",
                latest
            )



    # 去重

    result = {}


    for r in rows:

        result[r[0]] = r



    rows = list(
        result.values()
    )



    save_history(rows)



    print(
        "保存完成"
    )


    print(
        "总期数:",
        len(rows)
    )


    print(
        "最新:",
        rows[-1]
    )



if __name__ == "__main__":

    main()
