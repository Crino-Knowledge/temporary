# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Excel Editor Platform
# 使用 --onedir 模式（文件夹打包），启动速度比 --onefile 快很多，
# 因为 --onefile 每次运行都需要先解压到临时目录。
import os

block_cipher = None

a = Analysis(
    ['serve_web.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[('web', 'web')],
    hiddenimports=[
        'flask',
        'flask.json',
        'flask.templating',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.routing',
        'werkzeug.exceptions',
        'werkzeug.middleware.proxy_fix',
        'click',
        'jinja2',
        'jinja2.ext',
        'itsdangerous',
        'markupsafe',
        'importlib.metadata',
        'pkg_resources',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'numpy', 'pandas',
        'scipy', 'PIL', 'cv2', 'PyQt5', 'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],                     # onedir 模式：binaries/datas 不合并进 exe
    exclude_binaries=True,  # onedir 模式必须为 True
    name='Excel_Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,          # 无控制台窗口，日志写入 logs\ 目录
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# onedir 模式需要 COLLECT 把所有文件汇集到输出目录
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Excel_Editor',    # 输出目录名: dist\Excel_Editor\
)
