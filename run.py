import sys
import os
import streamlit.web.cli as stcli


def main():
    # 确保运行目录在 exe 所在的文件夹，这样才能正确读取 SQLite 数据库和关联文件夹
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
        os.chdir(os.path.dirname(sys.executable))
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(application_path)

    # 设定 Streamlit 启动参数：隐藏终端报错、自动在浏览器打开
    sys.argv = [
        "streamlit", "run", os.path.join(application_path, "app.py"),
        "--global.developmentMode=false",
        "--server.headless=false",  # 设为 false 让浏览器自动弹出来
    ]
    sys.exit(stcli.main())


if __name__ == '__main__':
    main()