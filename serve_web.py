# -*- coding: utf-8 -*-
"""
Excel 在线编辑平台 — 本地服务器
运行方式 (开发): python serve_web.py
运行方式 (打包): 双击 Excel在线编辑平台.exe
"""

import os
import sys
import socket
import logging
import threading
import webbrowser
import datetime
import urllib.parse

try:
    from flask import Flask, send_from_directory, request, jsonify, abort
    USE_FLASK = True
except ImportError:
    USE_FLASK = False


# ═══════════════════════════════════════════════════════
#  路径解析（兼容 PyInstaller --onefile 打包）
# ═══════════════════════════════════════════════════════

def get_resource_path(relative: str) -> str:
    """
    获取内嵌资源路径。
    - 开发模式：脚本所在目录
    - PyInstaller 打包后：临时解压目录 sys._MEIPASS
    """
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


def get_exe_dir() -> str:
    """
    获取 exe（或脚本）所在目录，用于写入日志、输出文件等可持久化数据。
    - 开发模式：脚本所在目录
    - PyInstaller 打包后：exe 所在目录（不是临时解压目录！）
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# ─── 目录常量 ───
WEB_DIR     = get_resource_path('web')
EXE_DIR     = get_exe_dir()
LOG_DIR     = os.path.join(EXE_DIR, 'logs')
OUTPUT_DIR  = os.path.join(EXE_DIR, 'output')
HTML_FILE   = 'Excel在线编辑平台.html'
DEFAULT_PORT = 8765

# ─── 创建必要目录 ───
os.makedirs(LOG_DIR,    exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════
#  日志系统（同时写文件和控制台）
# ═══════════════════════════════════════════════════════

_log_file = os.path.join(
    LOG_DIR,
    datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.log'
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(_log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger('excel_platform')

# 抑制 werkzeug 的冗余日志
logging.getLogger('werkzeug').setLevel(logging.WARNING)


# ═══════════════════════════════════════════════════════
#  工具函数
# ═══════════════════════════════════════════════════════

def find_free_port(start: int = DEFAULT_PORT, tries: int = 20) -> int:
    """从 start 向上寻找第一个空闲端口。"""
    for port in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f'未找到可用端口（{start}~{start + tries - 1}）')


def open_browser(port: int, delay: float = 1.5):
    """延迟后在默认浏览器中打开页面。"""
    def _open():
        import time
        time.sleep(delay)
        url = f'http://127.0.0.1:{port}'
        logger.info(f'正在打开浏览器：{url}')
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()


def check_html_exists():
    path = os.path.join(WEB_DIR, HTML_FILE)
    if not os.path.isfile(path):
        logger.error(f'未找到 HTML 文件：{path}')
        input('按 Enter 键退出…')
        sys.exit(1)


def safe_filename(name: str) -> str:
    """去除非法字符，防止路径穿越。"""
    name = urllib.parse.unquote(name)
    name = os.path.basename(name)
    # 替换 Windows 非法字符
    for ch in r'\/:*?"<>|':
        name = name.replace(ch, '_')
    return name or 'export.xlsx'


# ═══════════════════════════════════════════════════════
#  Flask 服务器
# ═══════════════════════════════════════════════════════

def build_flask_app() -> 'Flask':
    app = Flask(__name__)

    # ── 静态页面 ──
    @app.route('/')
    def index():
        return send_from_directory(WEB_DIR, HTML_FILE)

    @app.route('/<path:filename>')
    def static_file(filename):
        full = os.path.join(WEB_DIR, filename)
        if os.path.isfile(full):
            return send_from_directory(WEB_DIR, filename)
        abort(404)

    # ── API: 保存导出的 Excel 到 output/ 目录 ──
    @app.route('/api/save-excel', methods=['POST'])
    def save_excel():
        try:
            raw_name = request.headers.get('X-Filename', '')
            fname = safe_filename(raw_name) if raw_name else \
                f"export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            # 如果同名文件已存在，自动加时间戳后缀
            out_path = os.path.join(OUTPUT_DIR, fname)
            if os.path.exists(out_path):
                stem, ext = os.path.splitext(fname)
                stamp = datetime.datetime.now().strftime('%H%M%S')
                out_path = os.path.join(OUTPUT_DIR, f'{stem}_{stamp}{ext}')

            with open(out_path, 'wb') as f:
                f.write(request.get_data())

            logger.info(f'Excel 已保存 → {out_path}')
            return jsonify({'status': 'ok', 'path': out_path})
        except Exception as e:
            logger.error(f'保存 Excel 失败：{e}')
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # ── API: 接收前端日志 ──
    @app.route('/api/log', methods=['POST'])
    def client_log():
        try:
            data = request.get_json(silent=True) or {}
            level   = data.get('level', 'info').lower()
            message = data.get('message', '')
            fn = getattr(logger, level if level in ('debug','info','warning','error') else 'info')
            fn(f'[前端] {message}')
            return jsonify({'status': 'ok'})
        except Exception:
            return jsonify({'status': 'error'}), 500

    return app


def run_flask(port: int):
    app = build_flask_app()
    logger.info(f'Flask 服务器已启动 → http://127.0.0.1:{port}')
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)


# ═══════════════════════════════════════════════════════
#  内置 http.server 回退（无 Flask 时使用）
# ═══════════════════════════════════════════════════════

def run_builtin(port: int):
    import http.server

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=WEB_DIR, **kwargs)

        def do_GET(self):
            import urllib.parse as up
            if up.urlparse(self.path).path in ('/', ''):
                self.path = '/' + HTML_FILE
            super().do_GET()

        def log_message(self, fmt, *args):
            # 仅记录 HTML 请求，过滤静态资源
            msg = fmt % args
            if any(ext in msg for ext in ('.js','.css','.png','.ico','.woff','.map')):
                return
            logger.info(f'[HTTP] {msg}')

    server = http.server.HTTPServer(('127.0.0.1', port), Handler)
    logger.info(f'内置 HTTP 服务器已启动 → http://127.0.0.1:{port}')
    logger.warning('提示：内置服务器不支持 /api/save-excel，导出文件将只下载到浏览器，不会保存到 output/')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


# ═══════════════════════════════════════════════════════
#  主入口
# ═══════════════════════════════════════════════════════

def main():
    check_html_exists()

    port = find_free_port(DEFAULT_PORT)

    banner = f"""
{'=' * 54}
  Excel 在线编辑平台
{'=' * 54}
  访问地址  : http://127.0.0.1:{port}
  日志目录  : {LOG_DIR}
  导出目录  : {OUTPUT_DIR}
  后端引擎  : {'Flask' if USE_FLASK else '内置 http.server（建议安装 Flask）'}
  当前日志  : {_log_file}
{'─' * 54}
  按 Ctrl+C 或关闭此窗口可停止服务
{'=' * 54}
"""
    print(banner)
    logger.info('Excel 在线编辑平台 启动')
    logger.info(f'访问地址 : http://127.0.0.1:{port}')
    logger.info(f'日志文件 : {_log_file}')
    logger.info(f'导出目录 : {OUTPUT_DIR}')

    open_browser(port)

    try:
        if USE_FLASK:
            run_flask(port)
        else:
            run_builtin(port)
    except KeyboardInterrupt:
        logger.info('服务器已正常停止')
        print('\n[提示] 服务器已停止。')
    except OSError as e:
        logger.error(f'启动失败：{e}')
        input('按 Enter 键退出…')
        sys.exit(1)


if __name__ == '__main__':
    main()
