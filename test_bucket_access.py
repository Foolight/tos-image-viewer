#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 TOS Bucket 访问权限
"""
import tos
from tos.exceptions import TosClientError, TosServerError
from config import ACCESS_KEY_ID, ACCESS_KEY_SECRET, TOS_ENDPOINT_URL, REGION, BUCKET_NAME

print("=" * 70)
print("火山引擎 TOS Bucket 访问测试")
print("=" * 70)
print()

print("配置信息:")
print("-" * 70)
print(f"Access Key ID: {ACCESS_KEY_ID}")
print(f"Access Key Secret: {ACCESS_KEY_SECRET[:10]}...{ACCESS_KEY_SECRET[-10:]}")
print(f"Endpoint: {TOS_ENDPOINT_URL}")
print(f"Region: {REGION}")
print(f"Bucket: {BUCKET_NAME}")
print()
print("=" * 70)
print()

# 创建 TOS 客户端
try:
    client = tos.TosClientV2(
        ak=ACCESS_KEY_ID,
        sk=ACCESS_KEY_SECRET,
        endpoint=TOS_ENDPOINT_URL,
        region=REGION
    )
    print("✓ TOS 客户端创建成功")
    print()
except Exception as e:
    print(f"✗ TOS 客户端创建失败: {e}")
    exit(1)

# 测试1: 列出所有 Buckets
print("测试 1: 列出所有 Buckets")
print("-" * 70)
try:
    result = client.list_buckets()
    print(f"✓ 成功列出 Buckets")
    print(f"  找到 {len(result.buckets)} 个 Bucket:")
    for bucket in result.buckets:
        print(f"  - {bucket.name} (区域: {bucket.location}, 创建时间: {bucket.creation_date})")
        if bucket.name == BUCKET_NAME:
            print(f"    ✓ 找到目标 Bucket: {BUCKET_NAME}")
    print()
except TosServerError as e:
    print(f"✗ 失败: {e.message}")
    print(f"  错误代码: {e.code}")
    print(f"  状态码: {e.status_code}")
    print()
except Exception as e:
    print(f"✗ 失败: {e}")
    print()

# 测试2: 获取 Bucket 信息
print("测试 2: 获取 Bucket 信息")
print("-" * 70)
try:
    result = client.head_bucket(bucket=BUCKET_NAME)
    print(f"✓ Bucket '{BUCKET_NAME}' 存在且可访问")
    print(f"  Region: {result.region}")
    print()
except TosServerError as e:
    print(f"✗ 失败: {e.message}")
    print(f"  错误代码: {e.code}")
    print(f"  状态码: {e.status_code}")
    if e.code == 'NoSuchBucket':
        print(f"  提示: Bucket '{BUCKET_NAME}' 不存在")
    elif e.code == 'AccessDenied':
        print(f"  提示: 没有访问 Bucket '{BUCKET_NAME}' 的权限")
    print()
except Exception as e:
    print(f"✗ 失败: {e}")
    print()

# 测试3: 列出 Bucket 中的对象
print("测试 3: 列出 Bucket 中的对象")
print("-" * 70)
try:
    result = client.list_objects(bucket=BUCKET_NAME, max_keys=10)
    print(f"✓ 成功列出对象")

    if hasattr(result, 'contents') and result.contents:
        print(f"  找到 {len(result.contents)} 个对象（显示前10个）:")
        for obj in result.contents[:10]:
            print(f"  - {obj.key} (大小: {obj.size} 字节)")
    else:
        print(f"  Bucket 为空，没有对象")
    print()
except TosServerError as e:
    print(f"✗ 失败: {e.message}")
    print(f"  错误代码: {e.code}")
    print(f"  状态码: {e.status_code}")

    if e.code == 'AccessDenied':
        print()
        print("  可能的原因:")
        print("  1. Access Key 没有读取该 Bucket 的权限")
        print("  2. Bucket 的访问策略限制了访问")
        print("  3. Access Key 被禁用或已删除")
        print()
        print("  解决方法:")
        print("  - 登录火山引擎控制台")
        print("  - 检查 IAM 用户权限，确保有 TOS 读取权限")
        print("  - 检查 Bucket 的访问策略")
        print("  - 尝试给 IAM 用户添加 'TOSFullAccess' 策略")
    print()
except Exception as e:
    print(f"✗ 失败: {e}")
    print()

# 测试4: 尝试上传测试文件
print("测试 4: 测试上传权限（上传临时测试文件）")
print("-" * 70)
try:
    test_content = b"This is a test file"
    test_key = ".test_upload_permission.txt"

    result = client.put_object(
        bucket=BUCKET_NAME,
        key=test_key,
        content=test_content
    )
    print(f"✓ 上传测试文件成功")
    print(f"  文件: {test_key}")
    print(f"  ETag: {result.etag}")

    # 删除测试文件
    try:
        client.delete_object(bucket=BUCKET_NAME, key=test_key)
        print(f"✓ 删除测试文件成功")
    except:
        print(f"  注意: 测试文件 '{test_key}' 未能自动删除，请手动删除")
    print()

except TosServerError as e:
    print(f"✗ 失败: {e.message}")
    print(f"  错误代码: {e.code}")
    print(f"  状态码: {e.status_code}")

    if e.code == 'AccessDenied':
        print()
        print("  提示: 没有上传权限（只读权限）")
        print("  如果只需要查看图片，可以忽略此错误")
    print()
except Exception as e:
    print(f"✗ 失败: {e}")
    print()

print("=" * 70)
print("测试完成")
print("=" * 70)
print()
print("总结:")
print("-" * 70)
print("如果所有测试都失败，请检查:")
print("1. Access Key ID 和 Secret 是否正确")
print("2. Endpoint 和 Region 是否正确")
print("3. Bucket 名称是否正确")
print("4. IAM 用户是否有 TOS 访问权限")
print()
print("建议操作:")
print("1. 登录火山引擎控制台: https://console.volcengine.com")
print("2. 访问 IAM 用户管理: https://console.volcengine.com/iam/user/")
print("3. 给用户添加 'TOSFullAccess' 或 'TOSReadOnlyAccess' 策略")
print("4. 或者在 Bucket 设置中配置访问策略")
print("=" * 70)
