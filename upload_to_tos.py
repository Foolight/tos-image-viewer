#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图片上传到火山引擎 TOS 的脚本
"""
import os
import json
import datetime
from pathlib import Path
import tos
from tos.exceptions import TosClientError, TosServerError


class TOSUploader:
    """火山引擎 TOS 上传器"""

    def __init__(self, access_key_id, secret_access_key, endpoint, region, bucket_name):
        """
        初始化 TOS 上传器

        Args:
            access_key_id: Access Key ID
            secret_access_key: Secret Access Key (原始密钥，不需要解码)
            endpoint: TOS endpoint URL
            region: 区域
            bucket_name: 存储桶名称
        """
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key  # 直接使用原始密钥
        self.endpoint = endpoint
        self.region = region
        self.bucket_name = bucket_name

        # 创建 TOS 客户端
        self.client = tos.TosClientV2(
            ak=self.access_key_id,
            sk=self.secret_access_key,
            endpoint=self.endpoint,
            region=self.region
        )

        # 图片数据文件路径
        self.images_data_file = Path(__file__).parent / 'images_data.json'

    def _save_image_url(self, url, key, size=0):
        """保存图片URL到JSON文件"""
        try:
            # 读取现有数据
            if self.images_data_file.exists():
                with open(self.images_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'images': []}

            images = data.get('images', [])

            # 检查是否已存在
            if any(img['url'] == url for img in images):
                return True

            # 添加新图片
            new_image = {
                'key': key,
                'url': url,
                'size': size,
                'added_time': datetime.datetime.now().isoformat()
            }

            images.append(new_image)
            data['images'] = images

            # 保存
            with open(self.images_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"保存URL到列表失败: {e}")
            return False

    def upload_file(self, local_file_path, object_key=None, content_type=None):
        """
        上传单个文件到 TOS

        Args:
            local_file_path: 本地文件路径
            object_key: 对象存储的 key（文件名），如果不指定则使用本地文件名
            content_type: 文件的 MIME 类型，如果不指定会自动识别

        Returns:
            上传成功返回对象的 URL，失败返回 None
        """
        try:
            local_path = Path(local_file_path)

            # 检查文件是否存在
            if not local_path.exists():
                print(f"错误：文件不存在 - {local_file_path}")
                return None

            # 如果没有指定 object_key，使用文件名
            if object_key is None:
                object_key = local_path.name

            # 自动识别图片类型
            if content_type is None:
                ext = local_path.suffix.lower()
                content_types = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.bmp': 'image/bmp',
                    '.webp': 'image/webp',
                    '.svg': 'image/svg+xml',
                }
                content_type = content_types.get(ext, 'application/octet-stream')

            print(f"正在上传 {local_file_path} 到 {self.bucket_name}/{object_key}...")

            # 上传文件
            with open(local_file_path, 'rb') as f:
                result = self.client.put_object(
                    bucket=self.bucket_name,
                    key=object_key,
                    content=f,
                    content_type=content_type
                )

            # 构建文件 URL
            file_url = f"https://{self.bucket_name}.{self.endpoint}/{object_key}"

            print(f"上传成功！")
            print(f"ETag: {result.etag}")
            print(f"URL: {file_url}")

            # 获取文件大小
            file_size = local_path.stat().st_size

            # 保存URL到列表
            if self._save_image_url(file_url, object_key, file_size):
                print(f"已添加到图片列表")

            return file_url

        except TosClientError as e:
            print(f"客户端错误：{e}")
            return None
        except TosServerError as e:
            print(f"服务端错误：{e}")
            print(f"状态码：{e.status_code}")
            print(f"错误代码：{e.code}")
            print(f"错误消息：{e.message}")
            return None
        except Exception as e:
            print(f"未知错误：{e}")
            return None

    def upload_folder(self, folder_path, prefix=''):
        """
        批量上传文件夹中的所有图片

        Args:
            folder_path: 文件夹路径
            prefix: TOS 中的路径前缀（例如 'images/'）

        Returns:
            上传成功的文件 URL 列表
        """
        folder = Path(folder_path)

        if not folder.exists() or not folder.is_dir():
            print(f"错误：文件夹不存在 - {folder_path}")
            return []

        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}

        # 获取所有图片文件
        image_files = [
            f for f in folder.rglob('*')
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        if not image_files:
            print(f"在 {folder_path} 中没有找到图片文件")
            return []

        print(f"找到 {len(image_files)} 个图片文件，开始上传...")

        uploaded_urls = []
        for img_file in image_files:
            # 构建相对路径作为 object_key
            relative_path = img_file.relative_to(folder)
            object_key = f"{prefix}{relative_path}".replace('\\', '/')

            url = self.upload_file(str(img_file), object_key)
            if url:
                uploaded_urls.append(url)

        print(f"\n上传完成！成功上传 {len(uploaded_urls)}/{len(image_files)} 个文件")
        return uploaded_urls


def main():
    """主函数 - 示例用法"""

    # 从配置文件导入（或直接在这里配置）
    from config import (
        ACCESS_KEY_ID,
        ACCESS_KEY_SECRET,
        TOS_ENDPOINT_URL,
        REGION,
        BUCKET_NAME
    )

    # 创建上传器
    uploader = TOSUploader(
        access_key_id=ACCESS_KEY_ID,
        secret_access_key=ACCESS_KEY_SECRET,
        endpoint=TOS_ENDPOINT_URL,
        region=REGION,
        bucket_name=BUCKET_NAME
    )

    # 示例1：上传单个文件
    # uploader.upload_file('test.jpg', 'images/test.jpg')

    # 示例2：上传整个文件夹
    # 获取脚本所在目录，确保路径正确
    script_dir = Path(__file__).parent
    folder_path = script_dir / 'Images'  # Images 文件夹路径
    prefix = ''                          # 上传到 bucket 根目录（如需要子目录，可改为 'images/' 等）

    uploader.upload_folder(str(folder_path), prefix=prefix)


if __name__ == '__main__':
    main()
