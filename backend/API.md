# Wardrobe Backend API 文档

基础地址
- 本地默认: `http://127.0.0.1:8000`
- 统一前缀: `/api`

鉴权
- 除注册/登录外，均需 `Authorization: Bearer <access_token>`
- 登录返回 `access` 与 `refresh`
- 刷新使用 `refresh` 换新 `access`

通用错误格式
- `{"detail": "error message"}`

常见错误码
- `400` 参数错误/缺失
- `401` 未认证/登录失败/Token 无效
- `403` 已认证但权限不足
- `404` 资源不存在
- `500` 服务器异常

鉴权失败示例
```json
{ "detail": "Authentication credentials were not provided." }
```

权限不足示例
```json
{ "detail": "You do not have permission to perform this action." }
```

## 账号与鉴权 `/api/auth`

POST `/api/auth/user/register/`  
说明: 普通用户注册（`/api/auth/register/` 同义）  
请求体:
```json
{
  "username": "user1",
  "email": "user1@example.com",
  "password": "Passw0rd!"
}
```
响应 201:
```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com"
}
```

POST `/api/auth/user/login/`  
说明: 普通用户登录（`/api/auth/login/` 同义）  
请求体:
```json
{
  "username": "user1",
  "password": "Passw0rd!"
}
```
响应 200:
```json
{
  "refresh": "jwt-refresh",
  "access": "jwt-access"
}
```
失败 401:
```json
{ "detail": "No active account found with the given credentials" }
```

POST `/api/auth/admin/register/`  
说明: 管理员注册，仅管理员可调用（`is_staff=True`）  
请求体同普通注册  
响应 201: 同普通注册  
失败 401/403: 非管理员

POST `/api/auth/admin/login/`  
说明: 管理员登录，仅允许 `is_staff=True`  
请求体同普通登录  
响应 200: `refresh` + `access`  
失败 401:
```json
{ "detail": "Admin account required." }
```

POST `/api/auth/refresh/`  
请求体:
```json
{ "refresh": "jwt-refresh" }
```
响应 200:
```json
{ "access": "new-access", "refresh": "new-refresh" }
```

POST `/api/auth/logout/`  
说明: 刷新 token 拉黑  
请求体:
```json
{ "refresh": "jwt-refresh" }
```
响应 204: 无内容
失败 400:
```json
{ "detail": "refresh token required" }
```

GET `/api/auth/me/`  
说明: 获取当前用户信息  
响应 200:
```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com",
  "role": "user",
  "is_staff": false,
  "is_superuser": false
}
```

## 衣橱 `/api/wardrobe`

字段说明: `category` 取值为 `top` | `bottom` | `shoes`

GET `/api/wardrobe/items/`  
说明: 列表（当前用户）

POST `/api/wardrobe/items/`  
说明: 新建衣物  
请求体:
```json
{
  "category": "top",
  "item": "T恤",
  "style_semantics": ["休闲"],
  "season_semantics": ["夏季"],
  "usage_semantics": ["日常"],
  "color_semantics": "白色",
  "description": "基础款"
}
```

GET `/api/wardrobe/items/{id}/`  
PATCH `/api/wardrobe/items/{id}/`  
PUT `/api/wardrobe/items/{id}/`  
DELETE `/api/wardrobe/items/{id}/`

GET `/api/wardrobe/items/by-category/`  
说明: 按类分组  
响应 200:
```json
{
  "tops": [/* items */],
  "bottoms": [/* items */],
  "shoes": [/* items */]
}
```

POST `/api/wardrobe/items/upload/`  
说明: 上传图片并自动识别衣物  
Content-Type: `multipart/form-data`  
表单字段: `file` 或 `image`  
响应 201: ClothingItem

curl 示例:
```bash
curl -X POST http://127.0.0.1:8000/api/wardrobe/items/upload/ \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/image.png"
```

ClothingItem 响应示例:
```json
{
  "id": 1,
  "category": "top",
  "item": "T恤",
  "style_semantics": ["休闲"],
  "season_semantics": ["夏季"],
  "usage_semantics": ["日常"],
  "color_semantics": "白色",
  "description": "基础款",
  "image": "/media/items/xxx.png",
  "image_url": "http://127.0.0.1:8000/media/items/xxx.png",
  "created_at": "2026-03-04T12:00:00Z"
}
```

## 穿搭 `/api/outfits`

POST `/api/outfits/recommend/`  
说明: 基于天气与衣橱生成推荐  
请求体:
```json
{ "location": "101020100" }
```
响应 200:
```json
{
  "weather": { "temperature": 18.0, "feelsLike": 17.0, "condition": "多云", "icon": "101", "humidity": 60, "windDir": "东北风", "windScale": "2", "location": "上海", "obsTime": "2026-03-04T12:00:00Z" },
  "seasons": ["春季"],
  "outfit": { /* Outfit */ },
  "history": { /* OutfitHistory */ }
}
```
失败 400:
```json
{ "detail": "location required" }
```
失败 503:
```json
{ "detail": "weather unavailable" }
```

GET `/api/outfits/history/`  
POST `/api/outfits/history/`  
说明: 穿搭历史列表/创建  
创建请求体:
```json
{
  "outfit": 1,
  "rating": 5,
  "feedback": "很舒服"
}
```

GET `/api/outfits/history/{id}/`  
PATCH `/api/outfits/history/{id}/`  
PUT `/api/outfits/history/{id}/`  
DELETE `/api/outfits/history/{id}/`

Outfit 响应示例:
```json
{
  "id": 1,
  "top": 10,
  "bottom": 12,
  "shoes": null,
  "top_detail": { /* ClothingItem */ },
  "bottom_detail": { /* ClothingItem */ },
  "shoes_detail": null,
  "recommendation_text": "建议...",
  "weather": 2,
  "weather_detail": { /* WeatherSnapshot */ },
  "created_at": "2026-03-04T12:00:00Z"
}
```

OutfitHistory 响应示例:
```json
{
  "id": 1,
  "outfit": 1,
  "outfit_detail": { /* Outfit */ },
  "rating": 5,
  "feedback": "很舒服",
  "created_at": "2026-03-04T12:00:00Z"
}
```

WeatherSnapshot 响应示例:
```json
{
  "id": 2,
  "location": "上海",
  "temperature": 18.0,
  "feels_like": 17.0,
  "condition": "多云",
  "icon": "101",
  "humidity": 60,
  "wind_dir": "东北风",
  "wind_scale": "2",
  "obs_time": "2026-03-04T12:00:00Z",
  "raw": {},
  "created_at": "2026-03-04T12:00:00Z"
}
```

## 集成配置与天气 `/api/integrations`

GET `/api/integrations/config/`  
说明: 获取脱敏配置  
响应 200:
```json
{
  "api_base": "",
  "api_key_masked": "****",
  "has_api_key": false,
  "model": "",
  "removebg_api_key_masked": "****",
  "has_removebg_key": false,
  "bg_removal_method": "removebg",
  "qweather_api_key_masked": "****",
  "has_qweather_key": false,
  "qweather_api_host": "devapi.qweather.com"
}
```

POST `/api/integrations/config/`  
说明: 更新配置（返回未脱敏数据）  
请求体:
```json
{
  "api_base": "",
  "api_key": "",
  "model": "",
  "removebg_api_key": "",
  "bg_removal_method": "removebg",
  "qweather_api_key": "",
  "qweather_api_host": "devapi.qweather.com"
}
```
响应 200:
```json
{
  "message": "updated",
  "api_base": "",
  "api_key": "",
  "model": "",
  "removebg_api_key": "",
  "bg_removal_method": "removebg",
  "qweather_api_key": "",
  "qweather_api_host": "devapi.qweather.com"
}
```

GET `/api/integrations/weather/search/?query=beijing`  
说明: 城市搜索  
响应 200:
```json
[
  { "name": "北京", "id": "101010100", "adm1": "北京市", "adm2": "北京市", "country": "中国", "lat": "0", "lon": "0" }
]
```
失败 400:
```json
{ "detail": "query required" }
```

GET `/api/integrations/weather/now/?location=101020100`  
说明: 当前天气  
响应 200:
```json
{
  "temperature": 18.0,
  "feelsLike": 17.0,
  "condition": "多云",
  "icon": "101",
  "humidity": 60,
  "windDir": "东北风",
  "windScale": "2",
  "location": "上海",
  "obsTime": "2026-03-04T12:00:00Z"
}
```
失败 400:
```json
{ "detail": "location required" }
```
失败 503:
```json
{ "detail": "weather unavailable" }
```
