#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
火山引擎 TOS 图片浏览 API
"""
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import tos
from tos.exceptions import TosClientError, TosServerError
from config import ACCESS_KEY_ID, ACCESS_KEY_SECRET, TOS_ENDPOINT_URL, REGION, BUCKET_NAME

app = Flask(__name__, static_folder='static')
CORS(app)  # 允许跨域请求

# 创建 TOS 客户端
tos_client = tos.TosClientV2(
    ak=ACCESS_KEY_ID,
    sk=ACCESS_KEY_SECRET,
    endpoint=TOS_ENDPOINT_URL,
    region=REGION
)


@app.route('/')
def index():
    """主页"""
    return send_from_directory('static', 'index.html')


@app.route('/api/images')
def get_images():
    """
    获取图片列表 API
    支持分页参数：page（页码，从1开始）、page_size（每页数量）
    """
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))

        # 验证参数
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 50

        # 获取所有图片
        all_images = []
        marker = ''

        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}

        # 循环获取所有对象（处理分页）
        while True:
            try:
                if marker:
                    result = tos_client.list_objects(
                        bucket=BUCKET_NAME,
                        max_keys=1000,
                        marker=marker
                    )
                else:
                    result = tos_client.list_objects(
                        bucket=BUCKET_NAME,
                        max_keys=1000
                    )

                # 筛选图片文件
                if hasattr(result, 'contents') and result.contents:
                    for obj in result.contents:
                        # 检查文件扩展名
                        key = obj.key.lower()
                        if any(key.endswith(ext) for ext in image_extensions):
                            # 构建图片 URL
                            image_url = f"https://{BUCKET_NAME}.{TOS_ENDPOINT_URL}/{obj.key}"
                            all_images.append({
                                'key': obj.key,
                                'url': image_url,
                                'size': obj.size,
                                'last_modified': obj.last_modified.isoformat() if hasattr(obj, 'last_modified') else None
                            })

                # 检查是否还有更多数据
                if hasattr(result, 'is_truncated') and result.is_truncated:
                    marker = result.next_marker
                else:
                    break

            except TosServerError as e:
                return jsonify({
                    'success': False,
                    'error': f'TOS 服务器错误: {e.message}',
                    'code': e.code
                }), 500
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'获取图片列表失败: {str(e)}'
                }), 500

        # 按最后修改时间倒序排序（最新的在前面）
        all_images.sort(key=lambda x: x['last_modified'] or '', reverse=True)

        # 计算总数和总页数
        total = len(all_images)
        total_pages = (total + page_size - 1) // page_size  # 向上取整

        # 计算当前页的起始和结束索引
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        # 获取当前页的图片
        current_page_images = all_images[start_idx:end_idx]

        return jsonify({
            'success': True,
            'data': {
                'images': current_page_images,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total': total,
                    'total_pages': total_pages,
                    'has_prev': page > 1,
                    'has_next': page < total_pages
                }
            }
        })

    except TosClientError as e:
        return jsonify({
            'success': False,
            'error': f'TOS 客户端错误: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/download/<path:key>')
def download_image(key):
    """
    生成图片下载链接
    """
    try:
        # 生成预签名 URL（有效期1小时）
        url = tos_client.pre_signed_url(
            http_method='GET',
            bucket=BUCKET_NAME,
            key=key,
            expires=3600
        )

        return jsonify({
            'success': True,
            'download_url': url
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'生成下载链接失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("火山引擎 TOS 图片浏览器")
    print("=" * 60)
    print()
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Region: {REGION}")
    print()
    print("服务启动中...")
    print("访问地址: http://localhost:5000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)
