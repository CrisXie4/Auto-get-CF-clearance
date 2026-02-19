#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X.ai CF Clearance 一键获取
流程：打开页面 → 输入随机邮箱 → 点击 Next → 获取 CF clearance + 指纹
"""

import asyncio
import random
import string
import json
from playwright.async_api import async_playwright


def random_email():
    """生成随机邮箱"""
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(['gmail.com', 'outlook.com', 'yahoo.com', '163.com', 'qq.com'])
    return f"{name}@{domain}"


async def main():
    email = random_email()
    print(f"[*] 邮箱: {email}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.0.36"
        )
        
        # 隐藏自动化标记
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
        """)
        
        page = await context.new_page()
        
        # 1. 打开页面
        print("[*] 打开页面...")
        await page.goto("https://accounts.x.ai/sign-in?email=true", wait_until="networkidle")
        await asyncio.sleep(1)
        
        # 2. 输入邮箱
        print("[*] 输入邮箱...")
        input_box = await page.wait_for_selector('input[type="email"], input[name="email"], input', timeout=10000)
        await input_box.click()
        for char in email:
            await input_box.type(char, delay=random.randint(30, 80))
        
        await asyncio.sleep(0.5)
        
        # 3. 点击 Next
        print("[*] 点击 Next...")
        
        # 尝试多种方式点击 Next
        try:
            # 方式1: 文本匹配
            await page.get_by_text("Next", exact=False).click()
        except:
            try:
                # 方式2: role
                await page.get_by_role("button", name="Next").click()
            except:
                try:
                    # 方式3: CSS
                    await page.locator('button:has-text("Next")').click()
                except:
                    # 方式4: 按回车
                    await input_box.press("Enter")
        
        print("[*] 等待验证...")
        await asyncio.sleep(3)
        
        # 4. 获取 CF clearance
        print("[*] 获取 CF clearance...")
        cf_clearance = None
        
        for i in range(30):
            cookies = await context.cookies()
            for c in cookies:
                if c['name'] == 'cf_clearance':
                    cf_clearance = c['value']
                    print(f"[+] 成功获取! (等待{i+1}秒)")
                    break
            if cf_clearance:
                break
            await asyncio.sleep(1)
        
        # 5. 获取浏览器指纹
        fingerprint = await page.evaluate("""() => {
            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                hardwareConcurrency: navigator.hardwareConcurrency,
                screen: {width: screen.width, height: screen.height},
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            }
        }""")
        
        # 输出结果
        print("\n" + "="*60)
        print("结果")
        print("="*60)
        
        if cf_clearance:
            print(f"\n✅ CF Clearance:\n{cf_clearance}")
        else:
            print("\n❌ 未获取到 CF Clearance")
        
        print(f"\n📧 Email: {email}")
        print(f"\n🌐 User Agent:\n{fingerprint['userAgent']}")
        print(f"\n🔍 浏览器指纹:")
        print(f"   Platform: {fingerprint['platform']}")
        print(f"   Language: {fingerprint['language']}")
        print(f"   Timezone: {fingerprint['timezone']}")
        print(f"   Screen: {fingerprint['screen']['width']}x{fingerprint['screen']['height']}")
        print(f"   Cores: {fingerprint['hardwareConcurrency']}")
        
        # 保存
        result = {
            "email": email,
            "cf_clearance": cf_clearance,
            "user_agent": fingerprint['userAgent'],
            "fingerprint": fingerprint
        }
        
        with open(f"cf_{email.split('@')[0]}.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 已保存")
        print("="*60)
        
        await browser.close()
        return result


if __name__ == "__main__":
    asyncio.run(main())
