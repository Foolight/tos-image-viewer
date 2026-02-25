#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动添加图片URL到列表的工具
"""
import json
import datetime
from pathlib import Path
from urllib.parse import unquote

IMAGES_DATA_FILE = Path(__file__).parent / 'images_data.json'


def load_images():
    """加载图片列表"""
    if not IMAGES_DATA_FILE.exists():
        return []

    try:
        with open(IMAGES_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('images', [])
    except Exception as e:
        print(f"加载失败: {e}")
        return []


def save_images(images):
    """保存图片列表"""
    try:
        with open(IMAGES_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({'images': images}, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存失败: {e}")
        return False


def add_single_url(url):
    """添加单个URL"""
    images = load_images()

    # 检查是否已存在
    if any(img['url'] == url for img in images):
        print(f"❌ URL已存在")
        return False

    # 从URL中提取文件名
    key = url.split('/')[-1]
    key = unquote(key)  # URL解码

    # 添加新图片
    new_image = {
        'key': key,
        'url': url,
        'size': 0,
        'added_time': datetime.datetime.now().isoformat()
    }

    images.append(new_image)

    if save_images(images):
        print(f"✓ 添加成功: {key}")
        return True
    else:
        print(f"❌ 保存失败")
        return False


def add_multiple_urls(urls):
    """批量添加URL"""
    images = load_images()
    existing_urls = {img['url'] for img in images}

    added_count = 0

    for url in urls:
        url = url.strip()
        if not url:
            continue

        # 跳过已存在的
        if url in existing_urls:
            print(f"⊙ 跳过（已存在）: {url}")
            continue

        # 从URL中提取文件名
        key = url.split('/')[-1]
        key = unquote(key)

        new_image = {
            'key': key,
            'url': url,
            'size': 0,
            'added_time': datetime.datetime.now().isoformat()
        }

        images.append(new_image)
        existing_urls.add(url)
        added_count += 1
        print(f"✓ 添加: {key}")

    if save_images(images):
        print(f"\n成功添加 {added_count} 张图片")
        return True
    else:
        print(f"\n❌ 保存失败")
        return False


def list_images():
    """列出所有图片"""
    images = load_images()

    if not images:
        print("暂无图片")
        return

    print(f"\n共 {len(images)} 张图片:")
    print("=" * 80)

    for i, img in enumerate(images, 1):
        print(f"{i}. {img['key']}")
        print(f"   URL: {img['url']}")
        print(f"   添加时间: {img.get('added_time', 'N/A')}")
        print()


def clear_all():
    """清空所有图片"""
    confirm = input("确认要清空所有图片吗？(yes/no): ")

    if confirm.lower() in ['yes', 'y']:
        if save_images([]):
            print("✓ 已清空所有图片")
            return True
        else:
            print("❌ 清空失败")
            return False
    else:
        print("已取消")
        return False


def main():
    """主菜单"""
    print("=" * 60)
    print("图片 URL 管理工具")
    print("=" * 60)
    print()

    while True:
        print("\n请选择操作:")
        print("1. 添加单个图片URL")
        print("2. 批量添加图片URL（从文件）")
        print("3. 批量添加图片URL（手动输入）")
        print("4. 查看所有图片")
        print("5. 清空所有图片")
        print("0. 退出")
        print()

        choice = input("请输入选项 (0-5): ").strip()

        if choice == '1':
            print("\n添加单个图片URL")
            print("-" * 60)
            url = input("请输入图片URL: ").strip()

            if url:
                add_single_url(url)

        elif choice == '2':
            print("\n批量添加图片URL（从文件）")
            print("-" * 60)
            file_path = input("请输入URL列表文件路径: ").strip()

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]

                print(f"从文件读取到 {len(urls)} 个URL")
                add_multiple_urls(urls)

            except FileNotFoundError:
                print(f"❌ 文件不存在: {file_path}")
            except Exception as e:
                print(f"❌ 读取文件失败: {e}")

        elif choice == '3':
            print("\n批量添加图片URL（手动输入）")
            print("-" * 60)
            print("请输入图片URL，每行一个，输入空行结束:")

            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)

            if urls:
                print(f"\n准备添加 {len(urls)} 个URL")
                add_multiple_urls(urls)

        elif choice == '4':
            list_images()

        elif choice == '5':
            clear_all()

        elif choice == '0':
            print("\n再见！")
            break

        else:
            print("\n❌ 无效选项")


if __name__ == '__main__':
    main()
