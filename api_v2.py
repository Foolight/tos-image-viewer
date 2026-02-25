#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
火山引擎 TOS 图片浏览 API (基于URL列表)
不需要TOS列表权限，直接使用图片URL
"""
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import json
import os
from pathlib import Path
from urllib.parse import unquote

app = Flask(__name__, static_folder='static')
CORS(app)  # 允许跨域请求

# 图片数据文件路径
IMAGES_DATA_FILE = Path(__file__).parent / 'images_data.json'


def load_images():
    """从JSON文件加载图片列表"""
    if not IMAGES_DATA_FILE.exists():
        return []

    try:
        with open(IMAGES_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('images', [])
    except Exception as e:
        print(f"加载图片列表失败: {e}")
        return []


def save_images(images):
    """保存图片列表到JSON文件"""
    try:
        with open(IMAGES_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({'images': images}, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存图片列表失败: {e}")
        return False


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

        # 加载所有图片
        all_images = load_images()

        # 按添加时间倒序（最新的在前面）
        all_images.sort(key=lambda x: x.get('added_time', ''), reverse=True)

        # 计算总数和总页数
        total = len(all_images)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

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

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/add_image', methods=['POST'])
def add_image():
    """
    添加单个图片URL
    POST body: {"url": "https://...", "key": "image.jpg"}
    """
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': '缺少URL参数'
            }), 400

        url = data['url']
        key = data.get('key', '')

        # 如果没有提供key，从URL中提取
        if not key:
            key = url.split('/')[-1]
            key = unquote(key)  # URL解码

        # 加载现有图片列表
        images = load_images()

        # 检查是否已存在
        if any(img['url'] == url for img in images):
            return jsonify({
                'success': False,
                'error': '图片URL已存在'
            }), 400

        # 添加新图片
        import datetime
        new_image = {
            'key': key,
            'url': url,
            'size': data.get('size', 0),
            'added_time': datetime.datetime.now().isoformat()
        }

        images.append(new_image)

        # 保存
        if save_images(images):
            return jsonify({
                'success': True,
                'message': '图片添加成功',
                'image': new_image
            })
        else:
            return jsonify({
                'success': False,
                'error': '保存失败'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/batch_add_images', methods=['POST'])
def batch_add_images():
    """
    批量添加图片URL
    POST body: {"images": [{"url": "https://...", "key": "image.jpg"}, ...]}
    """
    try:
        data = request.get_json()

        if not data or 'images' not in data:
            return jsonify({
                'success': False,
                'error': '缺少images参数'
            }), 400

        new_images_data = data['images']

        if not isinstance(new_images_data, list):
            return jsonify({
                'success': False,
                'error': 'images必须是数组'
            }), 400

        # 加载现有图片列表
        images = load_images()
        existing_urls = {img['url'] for img in images}

        # 添加新图片
        import datetime
        added_count = 0

        for img_data in new_images_data:
            if 'url' not in img_data:
                continue

            url = img_data['url']

            # 跳过已存在的
            if url in existing_urls:
                continue

            key = img_data.get('key', '')
            if not key:
                key = url.split('/')[-1]
                key = unquote(key)

            new_image = {
                'key': key,
                'url': url,
                'size': img_data.get('size', 0),
                'added_time': datetime.datetime.now().isoformat()
            }

            images.append(new_image)
            existing_urls.add(url)
            added_count += 1

        # 保存
        if save_images(images):
            return jsonify({
                'success': True,
                'message': f'成功添加 {added_count} 张图片',
                'added_count': added_count
            })
        else:
            return jsonify({
                'success': False,
                'error': '保存失败'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/delete_image', methods=['POST'])
def delete_image():
    """
    删除图片
    POST body: {"url": "https://..."}
    """
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': '缺少URL参数'
            }), 400

        url = data['url']

        # 加载现有图片列表
        images = load_images()

        # 删除指定URL的图片
        original_count = len(images)
        images = [img for img in images if img['url'] != url]

        if len(images) == original_count:
            return jsonify({
                'success': False,
                'error': '图片不存在'
            }), 404

        # 保存
        if save_images(images):
            return jsonify({
                'success': True,
                'message': '图片删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '保存失败'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/clear_all', methods=['POST'])
def clear_all():
    """清空所有图片"""
    try:
        if save_images([]):
            return jsonify({
                'success': True,
                'message': '所有图片已清空'
            })
        else:
            return jsonify({
                'success': False,
                'error': '清空失败'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("火山引擎 TOS 图片浏览器 (基于URL列表)")
    print("=" * 60)
    print()
    print(f"图片数据文件: {IMAGES_DATA_FILE}")

    # 统计图片数量
    images = load_images()
    print(f"当前图片数量: {len(images)}")
    print()
    print("服务启动中...")

    # 支持云平台部署（使用环境变量PORT）
    port = int(os.environ.get('PORT', 5000))
    print(f"访问地址: http://localhost:{port}")
    print()
    print("API 接口:")
    print("  GET  /api/images           - 获取图片列表")
    print("  POST /api/add_image        - 添加单个图片")
    print("  POST /api/batch_add_images - 批量添加图片")
    print("  POST /api/delete_image     - 删除图片")
    print("  POST /api/clear_all        - 清空所有图片")
    print("=" * 60)

    # 生产环境不使用debug模式
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
