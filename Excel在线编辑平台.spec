# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置文件
# 用法：pyinstaller Excel在线编辑平台.spec --noconfirm --clean

import os

block_cipher = None

a = Analysis(
    ['serve_web.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    # 将 web/ 文件夹打包进 exe，运行时解压到临时目录
    datas=[('web', 'web')],
    hiddenimports=[
        # Flask 核心
        'flask',
        'flask.json',
        'flask.templating',
        # Werkzeug
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.routing',
        'werkzeug.exceptions',
        'werkzeug.middleware.proxy_fix',
        # 其他依赖
        'click',
        'jinja2',
        'jinja2.ext',
        'itsdangerous',
        'markupsafe',
        # 标准库补充
        'importlib.metadata',
        'pkg_resources',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的大型库，减小体积
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Excel_Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # 启用 UPX 压缩（需安装 upx，不影响功能）
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,       # 显示控制台窗口（可查看日志，Ctrl+C 停止服务）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 可选：指定图标（取消注释并放入 icon.ico）
    # icon='icon.ico',
)
