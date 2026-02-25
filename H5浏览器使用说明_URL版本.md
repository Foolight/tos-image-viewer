# H5 图片浏览器使用说明 (基于URL列表)

这个版本不需要TOS列表权限，直接使用图片的URL地址。

## 工作原理

- 上传图片后，自动将图片URL保存到 `images_data.json` 文件
- H5页面从JSON文件读取图片列表，不需要访问TOS
- 图片URL格式：`https://public-260224.tos-cn-beijing.volces.com/文件名.jpg`

## 快速开始

### 1. 启动服务

```bash
python api_v2.py
```

启动成功后访问：`http://localhost:5000`

### 2. 添加图片URL

有三种方式：

#### 方式1：上传时自动添加（推荐）

使用修改后的上传脚本，上传成功后会自动添加URL：

```bash
python upload_to_tos.py
```

上传成功后会显示：
```
上传成功！
ETag: ...
URL: https://public-260224.tos-cn-beijing.volces.com/xxx.jpg
已添加到图片列表
```

#### 方式2：使用管理工具

运行管理工具：

```bash
python add_images_url.py
```

菜单选项：
- **选项1**：添加单个URL
- **选项2**：从文件批量添加
- **选项3**：手动输入多个URL
- **选项4**：查看所有图片
- **选项5**：清空所有图片

#### 方式3：通过API添加

**添加单个图片：**

```bash
curl -X POST http://localhost:5000/api/add_image \
  -H "Content-Type: application/json" \
  -d '{"url": "https://public-260224.tos-cn-beijing.volces.com/image.jpg"}'
```

**批量添加图片：**

```bash
curl -X POST http://localhost:5000/api/batch_add_images \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      {"url": "https://public-260224.tos-cn-beijing.volces.com/image1.jpg"},
      {"url": "https://public-260224.tos-cn-beijing.volces.com/image2.jpg"}
    ]
  }'
```

## 使用示例

### 示例1：手动添加URL

```bash
python add_images_url.py
```

```
请选择操作:
1. 添加单个图片URL
> 1

请输入图片URL: https://public-260224.tos-cn-beijing.volces.com/test.jpg
✓ 添加成功: test.jpg
```

### 示例2：从文件批量添加

创建一个 `urls.txt` 文件，每行一个URL：

```
https://public-260224.tos-cn-beijing.volces.com/image1.jpg
https://public-260224.tos-cn-beijing.volces.com/image2.jpg
https://public-260224.tos-cn-beijing.volces.com/image3.jpg
```

然后导入：

```bash
python add_images_url.py
```

```
请选择操作:
2. 批量添加图片URL（从文件）
> 2

请输入URL列表文件路径: urls.txt
从文件读取到 3 个URL
✓ 添加: image1.jpg
✓ 添加: image2.jpg
✓ 添加: image3.jpg

成功添加 3 张图片
```

### 示例3：查看已添加的图片

```bash
python add_images_url.py
```

```
请选择操作:
4. 查看所有图片
> 4

共 3 张图片:
================================================================================
1. image1.jpg
   URL: https://public-260224.tos-cn-beijing.volces.com/image1.jpg
   添加时间: 2024-02-24T10:00:00

2. image2.jpg
   URL: https://public-260224.tos-cn-beijing.volces.com/image2.jpg
   添加时间: 2024-02-24T10:01:00

...
```

## API 接口说明

### GET /api/images

获取图片列表（支持分页）

**参数：**
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认50）

**返回：**
```json
{
  "success": true,
  "data": {
    "images": [
      {
        "key": "image.jpg",
        "url": "https://...",
        "size": 12345,
        "added_time": "2024-02-24T10:00:00"
      }
    ],
    "pagination": {
      "current_page": 1,
      "page_size": 50,
      "total": 100,
      "total_pages": 2,
      "has_prev": false,
      "has_next": true
    }
  }
}
```

### POST /api/add_image

添加单个图片

**请求体：**
```json
{
  "url": "https://public-260224.tos-cn-beijing.volces.com/image.jpg",
  "key": "image.jpg",  // 可选，不提供会自动从URL提取
  "size": 12345        // 可选
}
```

### POST /api/batch_add_images

批量添加图片

**请求体：**
```json
{
  "images": [
    {"url": "https://..."},
    {"url": "https://..."}
  ]
}
```

### POST /api/delete_image

删除图片

**请求体：**
```json
{
  "url": "https://..."
}
```

### POST /api/clear_all

清空所有图片

## 文件结构

```
huoshanTest/
├── api_v2.py              # 新的API服务器（基于URL列表）
├── static/
│   └── index.html         # H5前端页面（不需要修改）
├── images_data.json       # 图片URL列表（自动生成）
├── upload_to_tos.py       # 上传脚本（已修改，自动记录URL）
├── add_images_url.py      # URL管理工具
└── config.py              # 配置文件
```

## images_data.json 格式

```json
{
  "images": [
    {
      "key": "image.jpg",
      "url": "https://public-260224.tos-cn-beijing.volces.com/image.jpg",
      "size": 12345,
      "added_time": "2024-02-24T10:00:00"
    }
  ]
}
```

## 优势

✅ **不需要TOS列表权限**：只需要上传权限
✅ **图片URL可以公开访问**：直接使用HTTPS URL
✅ **简单易用**：上传即自动添加到列表
✅ **支持手动管理**：可以手动添加/删除URL
✅ **离线可用**：只要有URL列表就能浏览

## 注意事项

1. **图片必须可公开访问**：URL要能直接在浏览器打开
2. **URL格式**：`https://{bucket}.{endpoint}/{文件名}`
3. **自动去重**：相同URL不会重复添加
4. **文件名提取**：会自动从URL中提取文件名并URL解码
5. **排序**：按添加时间倒序（最新的在前）

## 常见问题

### Q: 上传图片后，H5页面看不到？

**A:** 刷新浏览器页面，或者检查 `images_data.json` 文件是否包含该图片URL。

### Q: 如何批量导入已上传的图片？

**A:**
1. 创建一个文本文件，每行一个图片URL
2. 使用 `add_images_url.py` 工具的选项2导入

### Q: 图片URL格式是什么？

**A:** `https://{bucket名称}.{endpoint}/{文件路径}`

示例：`https://public-260224.tos-cn-beijing.volces.com/test.jpg`

### Q: 可以删除图片URL吗？

**A:** 可以，使用API的 `/api/delete_image` 接口，或者直接编辑 `images_data.json` 文件。

### Q: 图片在TOS中删除了，但列表还在？

**A:** 需要手动从 `images_data.json` 中删除对应的URL，或使用API删除。

## 进阶使用

### 从现有bucket导出URL列表

如果你已经有很多图片在TOS中，可以创建一个脚本批量添加：

```python
# 示例：批量添加URL
urls = [
    "https://public-260224.tos-cn-beijing.volces.com/image1.jpg",
    "https://public-260224.tos-cn-beijing.volces.com/image2.jpg",
    # ... 更多URL
]

import requests
response = requests.post('http://localhost:5000/api/batch_add_images', json={
    'images': [{'url': url} for url in urls]
})
print(response.json())
```

### 定期同步

可以创建定时任务，定期从TOS同步URL列表（如果有权限）。

## 总结

这个版本完全基于URL列表，不需要TOS的列表权限。只要：

1. 上传图片时获得URL
2. 将URL添加到 `images_data.json`
3. 就可以在H5页面浏览

非常适合没有TOS完整权限的场景！
