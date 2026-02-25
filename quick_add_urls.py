#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速添加图片URL
直接在代码中编辑URL列表
"""
import json
import datetime
from pathlib import Path
from urllib.parse import unquote

# ========================================
# 在这里添加你的图片URL，每行一个
# ========================================
URLS = [
    # 示例（删除这行注释，添加你的URL）
    # "https://public-260224.tos-cn-beijing.volces.com/image1.jpg",
    # "https://public-260224.tos-cn-beijing.volces.com/image2.jpg",

    # 你的URL从这里开始添加：
    "https://public-260224.tos-cn-beijing.volces.com/output_cloth_pairs_male__012_gen_2_gen_3_M46_环卫工人_备选1__cloth_test_1.png",
]
# ========================================

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


def main():
    print("=" * 70)
    print("快速添加图片URL")
    print("=" * 70)
    print()

    # 过滤空URL和注释
    urls = [url.strip() for url in URLS if url.strip() and not url.strip().startswith('#')]

    if not urls:
        print("❌ 没有找到URL")
        print("请编辑 quick_add_urls.py 文件，在 URLS 列表中添加图片URL")
        return

    print(f"准备添加 {len(urls)} 个URL:")
    print("-" * 70)

    # 加载现有图片
    images = load_images()
    existing_urls = {img['url'] for img in images}

    added_count = 0
    skipped_count = 0

    for url in urls:
        # 从URL中提取文件名
        key = url.split('/')[-1]
        key = unquote(key)  # URL解码

        # 跳过已存在的
        if url in existing_urls:
            print(f"⊙ 跳过（已存在）: {key}")
            skipped_count += 1
            continue

        # 添加新图片
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

    print()
    print("-" * 70)

    # 保存
    if save_images(images):
        print(f"✓ 成功！")
        print(f"  新增: {added_count} 张")
        print(f"  跳过: {skipped_count} 张")
        print(f"  总计: {len(images)} 张")
        print()
        print("现在可以刷新浏览器查看图片了！")
    else:
        print(f"❌ 保存失败")

    print("=" * 70)


if __name__ == '__main__':
    main()
