#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Olist BI仪表板启动器
一键启动交互式商业智能仪表板
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """检查依赖包"""
    try:
        import streamlit
        import pandas
        import plotly
        print("✅ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("📦 正在安装依赖包...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements_dashboard.txt"
            ])
            print("✅ 依赖包安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖包安装失败，请手动安装:")
            print("pip3 install -r requirements_dashboard.txt")
            return False

def check_data_files():
    """检查数据文件"""
    required_files = [
        "data/seller_profile_processed.csv",
        "data/olist_orders_dataset.csv",
        "data/olist_order_items_dataset.csv",
        "data/olist_order_reviews_dataset.csv",
        "data/olist_products_dataset.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少以下数据文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ 所有数据文件已就绪")
    return True

def main():
    """主启动函数"""
    print("🚀 启动Olist商业智能仪表板")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        return
    
    # 检查数据文件
    if not check_data_files():
        print("\n💡 提示: 请先运行 data_exploration.py 生成处理后的数据文件")
        return
    
    # 启动Streamlit
    print("\n🌐 启动Web界面...")
    print("📊 仪表板将在浏览器中自动打开")
    print("🔗 如果没有自动打开，请访问: http://localhost:8501")
    print("\n⏹️  按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard/interactive_bi_dashboard.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 仪表板已停止")
    except FileNotFoundError:
        print("❌ Streamlit未找到，请安装: pip3 install streamlit")

if __name__ == "__main__":
    main() 