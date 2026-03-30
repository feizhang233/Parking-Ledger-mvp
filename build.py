import os
import subprocess
import platform


def build_app():
    print("🚀 停车记账本...")

    # 判断当前系统，Windows 的路径分隔符是 ';'，Mac/Linux 是 ':'
    separator = ";" if platform.system() == "Windows" else ":"

    # 设定需要一并打包进 exe 的资料夹和文件
    # 格式： "来源路径{分隔符}目标路径"
    add_data_args = [
        f"--add-data=app.py{separator}.",
        f"--add-data=init_sample_data.py{separator}.",
        f"--add-data=ledger{separator}ledger",
        f"--add-data=sql{separator}sql"
    ]

    # 组合 PyInstaller 指令
    command = [
                  "pyinstaller",
                  "--name=ParkingLedger",  # 生成的程序名称
                  "--onedir",  # 生成一个文件夹（包含 exe 和依赖），比单文件启动快很多且不易报错
                  "--noconfirm",  # 直接覆盖之前的打包文件
                  "--clean",  # 清理缓存
                  # 隐藏黑色终端视窗 (如果发现无法运行，可以先注释掉这行方便看报错)
                  "--windowed",
              ] + add_data_args + ["run.py"]

    # 执行打包
    subprocess.run(command)
    print("✅ 打包完成！请查看专案目录下的 'dist/ParkingLedger' 文件夹。")


if __name__ == "__main__":
    build_app()