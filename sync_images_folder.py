#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扫描 Images 文件夹，生成所有图片的URL并添加到列表
同时删除指定的图片
"""
import json
import datetime
from pathlib import Path
from urllib.parse import quote
import tos
from tos.exceptions import TosClientError, TosServerError
from config import ACCESS_KEY_ID, ACCESS_KEY_SECRET, TOS_ENDPOINT_URL, REGION, BUCKET_NAME

# 配置
IMAGES_FOLDER = Path(__file__).parent / 'Images'
IMAGES_DATA_FILE = Path(__file__).parent / 'images_data.json'
DELETE_FILES = ['^x^.jpg', '^x^.png', '^x^']  # 要删除的文件名（支持多个扩展名）

# 支持的图片格式
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}


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


def delete_image_from_tos(key):
    """从 TOS 删除图片"""
    try:
        client = tos.TosClientV2(
            ak=ACCESS_KEY_ID,
            sk=ACCESS_KEY_SECRET,
            endpoint=TOS_ENDPOINT_URL,
            region=REGION
        )

        client.delete_object(bucket=BUCKET_NAME, key=key)
        return True
    except TosServerError as e:
        if e.code == 'NoSuchKey':
            # 文件不存在，视为成功
            return True
        print(f"删除失败: {e.message}")
        return False
    except Exception as e:
        print(f"删除失败: {e}")
        return False


def main():
    print("=" * 70)
    print("扫描 Images 文件夹并生成图片URL列表")
    print("=" * 70)
    print()

    # 检查文件夹是否存在
    if not IMAGES_FOLDER.exists():
        print(f"❌ Images 文件夹不存在: {IMAGES_FOLDER}")
        return

    # 获取所有图片文件
    image_files = []
    for file_path in IMAGES_FOLDER.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            image_files.append(file_path)

    if not image_files:
        print(f"❌ Images 文件夹中没有找到图片文件")
        return

    print(f"找到 {len(image_files)} 个图片文件")
    print()

    # 加载现有图片列表
    images = load_images()
    existing_urls = {img['url'] for img in images}

    added_count = 0
    skipped_count = 0
    deleted_count = 0

    print("-" * 70)
    print("处理文件:")
    print("-" * 70)

    for file_path in image_files:
        # 获取相对于 Images 文件夹的路径
        relative_path = file_path.relative_to(IMAGES_FOLDER)
        # 转换为 TOS 的 key（使用 / 作为分隔符）
        key = str(relative_path).replace('\\', '/')

        # 检查是否需要删除
        file_name = file_path.name
        should_delete = False

        for delete_name in DELETE_FILES:
            if file_name == delete_name or file_name.startswith(delete_name + '.'):
                should_delete = True
                break

        if should_delete:
            print(f"🗑️  删除: {key}")

            # 从 TOS 删除
            if delete_image_from_tos(key):
                print(f"   ✓ 已从 TOS 删除")
            else:
                print(f"   ! TOS 删除失败（可能不存在）")

            # 删除本地文件
            try:
                file_path.unlink()
                print(f"   ✓ 已从本地删除")
                deleted_count += 1
            except Exception as e:
                print(f"   ! 本地删除失败: {e}")

            continue

        # 生成 URL（对文件名进行 URL 编码）
        # 注意：URL 中的路径需要编码，但斜杠不编码
        url_key = '/'.join(quote(part, safe='') for part in key.split('/'))
        url = f"https://{BUCKET_NAME}.{TOS_ENDPOINT_URL}/{url_key}"

        # 检查是否已存在
        if url in existing_urls:
            print(f"⊙ 跳过（已存在）: {key}")
            skipped_count += 1
            continue

        # 获取文件大小
        try:
            file_size = file_path.stat().st_size
        except:
            file_size = 0

        # 添加到列表
        new_image = {
            'key': key,
            'url': url,
            'size': file_size,
            'added_time': datetime.datetime.now().isoformat()
        }

        images.append(new_image)
        existing_urls.add(url)
        added_count += 1
        print(f"✓ 添加: {key}")
        print(f"   URL: {url}")

    print()
    print("-" * 70)
    print("处理完成!")
    print("-" * 70)
    print(f"新增: {added_count} 张")
    print(f"跳过: {skipped_count} 张")
    print(f"删除: {deleted_count} 张")
    print(f"总计: {len(images)} 张")
    print()

    # 保存
    if save_images(images):
        print("✓ 已保存到 images_data.json")
        print()
        print("现在可以访问 http://localhost:5000 查看图片了！")
        print("记得先启动服务: python api_v2.py")
    else:
        print("❌ 保存失败")

    print("=" * 70)


if __name__ == '__main__':
    main()
