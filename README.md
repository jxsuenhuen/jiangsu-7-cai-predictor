# 江苏7位数统计预测 V10

Windows 与 iPhone 共用的无依赖 PWA。官网开奖历史由 GitHub Actions 每小时第7、27、47分钟抓取，成功后提交并在同一工作流部署 GitHub Pages，避免机器人提交无法触发 push 工作流的问题。

## 使用

网址：https://jxsuenhuen.github.io/jiangsu-7-cai-predictor/

Windows：Edge / Chrome 打开网址，浏览器菜单中安装应用。iPhone：Safari 打开网址 → 分享 → 添加到主屏幕。

GitHub 仓库 Settings → Pages → Source 应选择 GitHub Actions。如工作流失败，在 Actions 查看错误；历史数据不因抓取失败而清空。

## 数据真实性

官网完整下载：https://api.js-lottery.com/lottery/downSevenData

官网近期含日期列表：https://api.js-lottery.com/wfzq/seven/data

当前官网可下载4768期（03060—26171），号码已与下载逐条对照，并修正旧数据6期。保留旧版346期更早记录，标明旧版未核验。不能把这部分称为官方全量数据。官网号码下载没有日期，早期日期保留旧版，未逐期核验。同步状态与覆盖范围见 data-status.json。官方覆盖范围内同一期号码以官网为准。

统计模型使用每位历史频率和近期加权频率。模型权重不是开奖概率，没有可靠证据证明能提高命中率。回测以每期首次点击预测的记录为准；命中表示对应位置相同的数量，不是奖金奖级。预计期号、日期未处理所有休市，须以官网为准。预测记录仅保存在当前设备。

## 验证与维护

运行 `python update_history.py` 更新官网数据；`python -m unittest discover -s tests` 校验；`node --check app.js` 检查语法；`python build.py` 生成部署目录。抓取只需Python标准库。初始历史保留在仓库，不依赖第三方接口。

GitHub 定时任务可能延迟，非实时开奖接口。网页每5分钟及回到前台时刷新已发布的数据；手动刷新不能触发后台抓取。push、定时及手动运行统一走同步→测试→提交→部署，避免旧快照覆盖新部署。
