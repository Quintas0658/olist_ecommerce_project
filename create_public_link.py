#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 创建Streamlit应用的公开访问链接
使用ngrok创建安全的公网隧道
"""

import subprocess
import time
import threading
import sys
import os
import signal

class PublicDashboard:
    def __init__(self):
        self.streamlit_process = None
        self.ngrok_process = None
        
    def check_ngrok_installed(self):
        """检查ngrok是否已安装"""
        try:
            result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def install_ngrok_instructions(self):
        """提供ngrok安装说明"""
        print("📦 ngrok未安装，请按以下步骤安装：")
        print("-" * 40)
        print("方法1 - 使用brew (macOS):")
        print("  brew install ngrok/ngrok/ngrok")
        print("")
        print("方法2 - 直接下载:")
        print("  1. 访问 https://ngrok.com/download")
        print("  2. 下载适合您系统的版本")
        print("  3. 解压并添加到PATH")
        print("")
        print("方法3 - 使用npm:")
        print("  npm install -g ngrok")
        print("-" * 40)
        
    def start_streamlit(self):
        """启动Streamlit应用"""
        print("🚀 启动Streamlit应用...")
        
        # 设置环境变量
        env = os.environ.copy()
        env['STREAMLIT_SERVER_HEADLESS'] = 'true'
        env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        cmd = [
            sys.executable,
            "-m", "streamlit", "run", "dashboard/app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ]
        
        self.streamlit_process = subprocess.Popen(
            cmd, 
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待应用启动
        time.sleep(5)
        print("✅ Streamlit应用已启动 (localhost:8501)")
        
    def start_ngrok(self):
        """启动ngrok隧道"""
        print("🌐 创建ngrok隧道...")
        
        cmd = ['ngrok', 'http', '8501']
        self.ngrok_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待ngrok启动
        time.sleep(3)
        
        # 获取公开URL
        try:
            result = subprocess.run(['curl', '-s', 'localhost:4040/api/tunnels'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                import json
                tunnels = json.loads(result.stdout)
                if tunnels.get('tunnels'):
                    public_url = tunnels['tunnels'][0]['public_url']
                    print("🎉 公开访问链接已生成!")
                    print("=" * 50)
                    print(f"🔗 公开链接: {public_url}")
                    print("=" * 50)
                    print("📝 注意事项:")
                    print("  • 此链接任何人都可以访问")
                    print("  • 链接在会话结束后失效")
                    print("  • 免费版ngrok有连接数限制")
                    print("  • 按Ctrl+C停止服务")
                    return public_url
        except Exception as e:
            print(f"⚠️ 无法获取ngrok URL: {e}")
            print("请访问 http://localhost:4040 查看ngrok状态")
            
        return None
    
    def run(self):
        """运行公开仪表板"""
        print("🌐 Olist BI Dashboard - 公开链接生成器")
        print("=" * 50)
        
        # 检查ngrok
        if not self.check_ngrok_installed():
            self.install_ngrok_instructions()
            return
        
        try:
            # 启动Streamlit
            self.start_streamlit()
            
            # 启动ngrok
            public_url = self.start_ngrok()
            
            if public_url:
                print("\n🎯 仪表板正在运行...")
                print("按Ctrl+C停止服务")
                
                # 保持运行直到用户中断
                while True:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n⏹️ 正在停止服务...")
            self.cleanup()
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            self.cleanup()
    
    def cleanup(self):
        """清理进程"""
        if self.streamlit_process:
            self.streamlit_process.terminate()
            print("✅ Streamlit已停止")
            
        if self.ngrok_process:
            self.ngrok_process.terminate()
            print("✅ ngrok隧道已关闭")

def main():
    dashboard = PublicDashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 