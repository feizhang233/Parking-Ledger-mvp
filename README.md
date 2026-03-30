# 停車管理月度經營台帳 MVP

本專案是一個本地可運行的 Python 3 小工具，使用 Streamlit + SQLite 實現：

- 北京 / 外地分組 Project 管理
- Template 模板管理，新建 Project 可直接套用欄位
- 每個 Project 自定義欄位
- 折線圖查看每月收入、支出、利潤
- 欄位類型支援 income / expense / text
- 歷史台帳表格直接編輯
- 導出 Excel、單個 Project 設定包、整體系統設定包
- 支援簡體中文、繁體中文、英文切換

## 啟動

```bash
cd /Users/zhangfei/Documents/parking_ledger_mvp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 init_sample_data.py
streamlit run app.py
```
