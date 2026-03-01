# -*- coding: utf-8 -*-
"""
打包脚本 - 使用方法:
  python build.py
或双击运行（如果 .py 已关联 Python）
"""
import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd, desc=""):
    print(f"\n>>> {desc or ' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"\n[FAILED] returncode={result.returncode}")
        input("Press Enter to exit...")
        sys.exit(result.returncode)
    print("[OK]")

def main():
    print("=" * 50)
    print("  Excel Editor - Build Script")
    print("=" * 50)

    # --- 确定 Python ---
    venv_py = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
    if os.path.isfile(venv_py):
        python = venv_py
        print(f"[INFO] Using virtualenv: {venv_py}")
    else:
        python = sys.executable
        print(f"[INFO] Using system Python: {python}")

    pip_cmd = [python, "-m", "pip"]

    # --- 检查 Python ---
    run([python, "--version"], "Check Python version")

    # --- 安装依赖 ---
    run(pip_cmd + ["install", "flask", "pyinstaller", "--quiet",
                   "--disable-pip-version-check"],
        "Install flask + pyinstaller")

    # --- 下载前端资源（离线化，消除 CDN 卡顿）---
    lib_dir = os.path.join(BASE_DIR, 'web', 'lib')
    assets_ok = all(
        os.path.isfile(os.path.join(lib_dir, f))
        for f in ['tailwind.min.js', 'iconify.min.js', 'xlsx.full.min.js']
    )
    if assets_ok:
        print("\n>>> 前端离线资源已存在，跳过下载 [OK]")
    else:
        run([python, os.path.join(BASE_DIR, 'download_assets.py')],
            "Download frontend assets (offline mode)")

    # --- 清理旧构建 ---
    print("\n>>> Clean old build files")

    def _force_rmtree(path):
        """删除目录，自动处理只读文件；若被进程占用则提示用户重试。"""
        import stat, time
        def _onerror(func, fpath, exc_info):
            # 尝试去掉只读属性后重试
            try:
                os.chmod(fpath, stat.S_IWRITE)
                func(fpath)
            except Exception:
                pass
        for attempt in range(1, 4):
            try:
                shutil.rmtree(path, onerror=_onerror)
                return
            except PermissionError as e:
                print(f"\n  [警告] 无法删除旧文件（第 {attempt}/3 次）：")
                print(f"  {e}")
                print("\n  ► 请关闭正在运行的 Excel_Editor.exe（任务管理器中也要结束），")
                print("    然后按 Enter 键重试，或按 Ctrl+C 中止。")
                try:
                    input()
                except KeyboardInterrupt:
                    print("\n已中止。")
                    sys.exit(1)
        print("\n[FAILED] 多次尝试后仍无法删除旧目录，请手动删除后重试：")
        print(f"  {path}")
        input("Press Enter to exit...")
        sys.exit(1)

    for d in ["build"]:
        p = os.path.join(BASE_DIR, d)
        if os.path.isdir(p):
            _force_rmtree(p)
            print(f"  removed: {p}")
    # onedir 模式输出在 dist\Excel_Editor\ 子目录
    old_dir = os.path.join(BASE_DIR, "dist", "Excel_Editor")
    if os.path.isdir(old_dir):
        _force_rmtree(old_dir)
        print(f"  removed: {old_dir}")
    print("[OK]")

    # --- 运行 PyInstaller ---
    spec_file = os.path.join(BASE_DIR, "Excel_Editor.spec")
    run([python, "-m", "PyInstaller", spec_file,
         "--noconfirm", "--clean"],
        "PyInstaller packaging (onedir mode)")

    # --- 创建输出目录 ---
    print("\n>>> Create dist folder structure")
    app_dir = os.path.join(BASE_DIR, "dist", "Excel_Editor")
    for sub in ["logs", "output"]:
        p = os.path.join(app_dir, sub)
        os.makedirs(p, exist_ok=True)
        print(f"  created: {p}")

    # --- 写入 README ---
    readme = os.path.join(app_dir, "README.txt")
    with open(readme, "w", encoding="utf-8") as f:
        f.write("""\
Excel Editor Platform - README
================================

HOW TO START:
  Double-click "Excel_Editor.exe"
  The browser will open automatically.
  Close the window to stop the server.

FOLDERS:
  logs\\    Server logs (new file each run)
  output\\ Excel files exported from the platform

NOTES:
  - No Python or internet required on target PC
  - All frontend assets are bundled offline
  - Exported files are saved to output\\ as backup

DISTRIBUTE:
  Copy the entire "Excel_Editor" folder to any Windows PC.
  Do NOT move Excel_Editor.exe out of its folder.
""")
    print("[OK]")

    # --- 完成 ---
    exe_path = os.path.join(app_dir, "Excel_Editor.exe")
    print("\n" + "=" * 50)
    print("  BUILD SUCCESSFUL!")
    print("=" * 50)
    print(f"  目录   : {app_dir}")
    print(f"  EXE    : {exe_path}")
    print(f"  logs   : {os.path.join(app_dir, 'logs')}")
    print(f"  output : {os.path.join(app_dir, 'output')}")
    print("\n  将整个 dist\\Excel_Editor\\ 文件夹复制给其他人使用。")
    print("  注意: exe 必须留在文件夹内，不可单独复制！")
    print("=" * 50)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
