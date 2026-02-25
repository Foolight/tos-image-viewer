#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试火山引擎 TOS 密钥是否正确
"""
import base64
import tos
from tos.exceptions import TosClientError, TosServerError

# 从配置文件导入
from config import ACCESS_KEY_ID, ACCESS_KEY_SECRET, TOS_ENDPOINT_URL, REGION, BUCKET_NAME

print("=" * 60)
print("火山引擎 TOS 密钥测试")
print("=" * 60)
print()

print(f"Access Key ID: {ACCESS_KEY_ID}")
print(f"Secret Access Key (原始): {ACCESS_KEY_SECRET}")
print()

# 尝试解码 Base64
try:
    decoded_secret = base64.b64decode(ACCESS_KEY_SECRET).decode('utf-8')
    print(f"Secret Access Key (Base64解码后): {decoded_secret}")
    print()
except Exception as e:
    print(f"Base64 解码失败: {e}")
    decoded_secret = None
    print()

print(f"Endpoint: {TOS_ENDPOINT_URL}")
print(f"Region: {REGION}")
print(f"Bucket: {BUCKET_NAME}")
print()
print("=" * 60)
print()

# 测试1: 使用原始的 ACCESS_KEY_SECRET（不解码）
print("测试 1: 使用原始 Secret Access Key（不进行Base64解码）")
print("-" * 60)
try:
    client1 = tos.TosClientV2(
        ak=ACCESS_KEY_ID,
        sk=ACCESS_KEY_SECRET,  # 直接使用原始值
        endpoint=TOS_ENDPOINT_URL,
        region=REGION
    )

    # 尝试列出 bucket（测试连接）
    result = client1.list_objects(bucket=BUCKET_NAME, max_keys=1)
    print("✓ 成功！原始密钥是正确的")
    print(f"  Bucket '{BUCKET_NAME}' 可以访问")
    print()
    print("【结论】请修改 upload_to_tos.py，不要进行 Base64 解码")
    test1_success = True
except TosServerError as e:
    print(f"✗ 失败: {e.message}")
    print(f"  错误代码: {e.code}")
    print(f"  状态码: {e.status_code}")
    test1_success = False
except Exception as e:
    print(f"✗ 失败: {e}")
    test1_success = False

print()
print("=" * 60)
print()

# 测试2: 使用解码后的 ACCESS_KEY_SECRET
if decoded_secret:
    print("测试 2: 使用 Base64 解码后的 Secret Access Key")
    print("-" * 60)
    try:
        client2 = tos.TosClientV2(
            ak=ACCESS_KEY_ID,
            sk=decoded_secret,  # 使用解码后的值
            endpoint=TOS_ENDPOINT_URL,
            region=REGION
        )

        # 尝试列出 bucket
        result = client2.list_objects(bucket=BUCKET_NAME, max_keys=1)
        print("✓ 成功！解码后的密钥是正确的")
        print(f"  Bucket '{BUCKET_NAME}' 可以访问")
        print()
        print("【结论】当前代码的 Base64 解码逻辑是正确的")
        test2_success = True
    except TosServerError as e:
        print(f"✗ 失败: {e.message}")
        print(f"  错误代码: {e.code}")
        print(f"  状态码: {e.status_code}")
        test2_success = False
    except Exception as e:
        print(f"✗ 失败: {e}")
        test2_success = False
else:
    test2_success = False

print()
print("=" * 60)
print()
print("测试总结:")
print("-" * 60)
if test1_success:
    print("✓ 使用原始密钥（不解码）: 成功")
    print()
    print("请运行以下命令修复问题:")
    print("需要修改 upload_to_tos.py，移除 Base64 解码逻辑")
elif test2_success:
    print("✓ 使用解码后的密钥: 成功")
    print()
    print("当前代码应该可以正常工作")
else:
    print("✗ 两种方式都失败了")
    print()
    print("可能的问题:")
    print("1. Access Key ID 或 Secret Access Key 不正确")
    print("2. Bucket 名称不正确")
    print("3. 没有访问该 Bucket 的权限")
    print("4. Endpoint 或 Region 配置不正确")
    print()
    print("请检查:")
    print("- 在火山引擎控制台确认密钥是否正确")
    print("- 确认 Bucket 名称是否为 'public-260224'")
    print("- 确认该密钥有访问该 Bucket 的权限")

print("=" * 60)
