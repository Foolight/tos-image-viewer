#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
火山引擎 TOS 图片上传示例
"""

from upload_to_tos import TOSUploader
from config import ACCESS_KEY_ID, ACCESS_KEY_SECRET, TOS_ENDPOINT_URL, REGION, BUCKET_NAME


def example_single_file_upload():
    """示例：上传单个文件"""
    # 创建上传器
    uploader = TOSUploader(
        access_key_id=ACCESS_KEY_ID,
        secret_access_key=ACCESS_KEY_SECRET,
        endpoint=TOS_ENDPOINT_URL,
        region=REGION,
        bucket_name=BUCKET_NAME
    )

    # 上传单个文件
    # 参数1: 本地文件路径
    # 参数2: TOS 中的对象键（可选，默认使用文件名）
    url = uploader.upload_file(
        local_file_path='test.jpg',
        object_key='images/test.jpg'  # 可选：指定在 TOS 中的路径
    )

    if url:
        print(f"文件上传成功，访问地址：{url}")


def example_folder_upload():
    """示例：批量上传文件夹中的所有图片"""
    uploader = TOSUploader(
        access_key_id=ACCESS_KEY_ID,
        secret_access_key=ACCESS_KEY_SECRET,
        endpoint=TOS_ENDPOINT_URL,
        region=REGION,
        bucket_name=BUCKET_NAME
    )

    # 上传整个文件夹
    # 参数1: 本地文件夹路径
    # 参数2: TOS 中的路径前缀（可选）
    urls = uploader.upload_folder(
        folder_path='./images',
        prefix='uploads/'  # 可选：所有文件都会上传到 uploads/ 目录下
    )

    print(f"\n成功上传 {len(urls)} 个文件")
    for url in urls:
        print(f"- {url}")


def example_custom_upload():
    """示例：自定义上传配置"""
    # 也可以直接在代码中指定配置，而不使用 config.py
    uploader = TOSUploader(
        access_key_id='your_access_key_id',
        secret_access_key='your_secret_access_key',
        endpoint='tos-cn-beijing.volces.com',
        region='cn-beijing',
        bucket_name='your-bucket-name'
    )

    # 上传文件并指定 Content-Type
    url = uploader.upload_file(
        local_file_path='photo.png',
        object_key='photos/photo.png',
        content_type='image/png'
    )


if __name__ == '__main__':
    print("火山引擎 TOS 图片上传示例")
    print("=" * 50)
    print()
    print("请根据需要取消注释以下函数调用：")
    print()

    # 示例1：上传单个文件
    # example_single_file_upload()

    # 示例2：批量上传文件夹
    # example_folder_upload()

    # 示例3：自定义上传配置
    # example_custom_upload()

    print("使用前请：")
    print("1. 修改 config.py 中的 BUCKET_NAME 为你的实际 bucket 名称")
    print("2. 确保已安装依赖：pip install -r requirements.txt")
    print("3. 准备好要上传的图片文件")
