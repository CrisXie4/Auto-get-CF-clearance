```markdown
# X.ai CF Clearance 自动获取工具

一键获取 X.ai (Grok) 的 Cloudflare clearance cookie 和浏览器指纹信息，用于 API 渠道配置。

## 功能特点

- ✅ 自动打开 X.ai 登录页面
- ✅ 自动生成随机邮箱地址
- ✅ 自动输入邮箱并提交
- ✅ 自动等待 Cloudflare Turnstile 验证
- ✅ 自动提取 `cf_clearance` cookie
- ✅ 自动采集完整浏览器指纹
- ✅ 保存结果为 JSON 格式
- ✅ 输出 curl 可用格式

## 安装依赖

```bash
# 安装 Python 包
pip install playwright

# 安装浏览器（首次运行必需）
playwright install chromium
```

使用方法

基础运行

```bash
python xai_cf_clearance.py
```

运行流程

1. 自动打开浏览器窗口访问 `https://accounts.x.ai/sign-in?email=true`
2. 在页面输入框中输入随机生成的邮箱地址
3. 自动点击 Next 按钮提交
4. 等待 Cloudflare Turnstile 验证框出现并完成验证
5. 自动提取 `cf_clearance` cookie
6. 采集浏览器指纹信息
7. 保存结果并关闭浏览器

输出示例

```
🚀 X.ai CF Clearance 获取工具
============================================================
[*] 邮箱: abc123def@outlook.com
[*] 打开页面...
[*] 输入邮箱...
[*] 点击 Next...
[*] 等待验证...
[+] 成功获取! (等待3秒)

============================================================
结果
============================================================

✅ CF Clearance:
eSzYXTq2x9KLYqsnca7Duhm1gNSoB1QrSaGZE-1771487623-1.2.1.1-...

📧 Email: abc123def@outlook.com

🌐 User Agent:
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36...

🔍 浏览器指纹:
   Platform: Win32
   Language: zh-CN
   Timezone: Etc/GMT-8
   Screen: 1920x1080
   Cores: 8

💾 已保存
============================================================
```

输出文件

运行后会生成两个文件：

文件	说明	
`cf_[邮箱前缀].json`	完整结果（JSON格式）	
控制台输出	可直接复制的 cookie 和指纹	

JSON 结构

```json
{
  "email": "abc123def@outlook.com",
  "cf_clearance": "完整的clearance字符串",
  "user_agent": "Mozilla/5.0...",
  "fingerprint": {
    "userAgent": "...",
    "platform": "Win32",
    "language": "zh-CN",
    "hardwareConcurrency": 8,
    "screen": {"width": 1920, "height": 1080},
    "timezone": "Etc/GMT-8"
  }
}
```

在 NewAPI 中使用

1. 渠道配置

将获取到的 `cf_clearance` 填入 NewAPI 的渠道 Cookies 字段：

```
cf_clearance=eSzYXTq2x9KLYqPTwI9dsnca7Duhm1gNSoB1QrSaGZE-1771487623-1.2.1.1-...
```

2. 配合 curl_cffi 使用

```python
from curl_cffi import requests

CF_CLEARANCE = "你的clearance值"

r = requests.get(
    "https://api.x.ai/v1/models",
    cookies={"cf_clearance": CF_CLEARANCE},
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36..."
    },
    impersonate="chrome131",
)
```

注意事项

问题	解决方案	
CF Clearance 过期	重新运行脚本获取新的 cookie	
验证不通过	确保 `headless=False` 能看到浏览器窗口	
找不到输入框	页面结构可能变化，检查截图 `step*.png`	
获取失败	增加 `max_wait` 时间或检查网络连接	

故障排查

启用调试截图

脚本已内置自动截图功能，如果出现问题会保存：
- `step1_initial.png` - 初始页面
- `step2_after_click.png` - 点击 Next 后
- `error_final.png` - 错误状态

常见错误

`未获取到 CF Clearance`
- 等待时间不够 → 增加 `max_wait` 值
- 验证被拦截 → 检查 IP 是否被拉黑
- 页面未加载 → 检查网络连接

`找不到邮箱输入框`
- 页面加载失败 → 刷新重试
- 选择器失效 → 更新 `selectors` 列表

技术细节

浏览器指纹采集

脚本采集以下指纹信息：
- User Agent
- Platform
- Language/Languages
- Hardware Concurrency (CPU核心数)
- Device Memory
- Screen Resolution
- Timezone
- WebDriver 状态
- Plugins 列表

反检测措施

- 禁用 `AutomationControlled` 标记
- 隐藏 `navigator.webdriver`
- 模拟真实鼠标点击和键盘输入
- 添加随机延迟模拟人类操作

