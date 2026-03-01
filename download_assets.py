# -*- coding: utf-8 -*-
"""
下载前端 CDN 依赖到 web/lib/ 目录，实现完全离线运行。
运行方式:  python download_assets.py
"""
import os
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR  = os.path.join(BASE_DIR, 'web', 'lib')

ASSETS = [
    {
        'url' : 'https://cdn.tailwindcss.com',
        'dest': 'tailwind.min.js',
        'desc': 'Tailwind CSS Play CDN',
    },
    {
        'url' : 'https://cdn.jsdelivr.net/npm/@iconify/iconify@3.1.1/dist/iconify.min.js',
        'dest': 'iconify.min.js',
        'desc': 'Iconify 3.1.1',
    },
    {
        'url' : 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js',
        'dest': 'xlsx.full.min.js',
        'desc': 'SheetJS xlsx 0.18.5',
    },
]


def download(url: str, dest: str, desc: str):
    print(f'  下载 {desc} ...', end=' ', flush=True)
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    with open(dest, 'wb') as f:
        f.write(data)
    size_kb = len(data) / 1024
    print(f'完成  ({size_kb:.0f} KB)')


def main():
    os.makedirs(LIB_DIR, exist_ok=True)
    print(f'目标目录: {LIB_DIR}\n')

    failed = []
    for asset in ASSETS:
        dest_path = os.path.join(LIB_DIR, asset['dest'])
        try:
            download(asset['url'], dest_path, asset['desc'])
        except Exception as e:
            print(f'失败: {e}')
            failed.append(asset['desc'])

    print()
    if failed:
        print(f'[警告] 以下资源下载失败，请检查网络后重试:')
        for name in failed:
            print(f'  - {name}')
        sys.exit(1)
    else:
        print('[成功] 全部资源已下载，可离线运行。')


if __name__ == '__main__':
    main()
