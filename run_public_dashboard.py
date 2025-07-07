#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Olist BI Dashboard - 公开访问版本
Public Access Dashboard Runner
"""

import subprocess
import sys
import os

def run_public_dashboard():
    """运行可公开访问的仪表板"""
    print("🚀 启动Olist BI Dashboard (公开访问模式)")
    print("=" * 50)
    
    # 设置环境变量以避免认证
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    try:
        # 运行streamlit应用
        cmd = [
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            "dashboard/app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",  # 允许外部访问
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ]
        
        print("📡 启动命令:", " ".join(cmd))
        print("🌐 访问地址: http://localhost:8501")
        print("🔗 网络访问: http://0.0.0.0:8501")
        print("=" * 50)
        
        # 启动应用
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n⏹️ 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    run_public_dashboard() 