#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Olist E-commerce BI Dashboard 启动器
一键启动交互式商业智能分析平台
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖...")
    
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'numpy', 
        'scikit-learn', 'seaborn', 'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", "requirements_dashboard.txt"
            ])
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return False
    
    return True

def check_data_files():
    """检查数据文件"""
    print("\n📁 检查数据文件...")
    
    # 检查原始数据
    data_paths = ['data/', 'archive/']
    data_files = [
        'olist_sellers_dataset.csv',
        'olist_orders_dataset.csv', 
        'olist_order_items_dataset.csv'
    ]
    
    data_found = False
    for path in data_paths:
        if os.path.exists(path):
            files_in_path = os.listdir(path)
            if any(f in files_in_path for f in data_files):
                print(f"   ✅ 在 {path} 找到数据文件")
                data_found = True
                break
    
    if not data_found:
        print("   ⚠️ 未找到原始数据文件")
        print("   请将CSV文件放在 data/ 或 archive/ 目录中")
    
    # 检查处理后的数据
    processed_data = 'data/seller_profile_processed.csv'
    if os.path.exists(processed_data):
        print(f"   ✅ 找到处理后的数据: {processed_data}")
    else:
        print(f"   ⚠️ 未找到处理后的数据，启动时将自动生成")
    
    return True

def run_dashboard():
    """启动Dashboard"""
    print("\n🚀 启动Streamlit Dashboard...")
    
    # 确保dashboard文件存在
    dashboard_file = "dashboard/app.py"
    if not os.path.exists(dashboard_file):
        print(f"❌ 未找到Dashboard文件: {dashboard_file}")
        return False
    
    try:
        # 启动Streamlit
        cmd = [
            "streamlit", "run", dashboard_file,
            "--server.port=8502",
            "--server.address=localhost"
        ]
        
        print("🌐 Dashboard将在 http://localhost:8502 启动")
        print("📱 移动端友好设计，支持响应式布局")
        print("🔧 使用 Ctrl+C 停止服务")
        print("-" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard已停止")
        return True
    except FileNotFoundError:
        print("❌ Streamlit未安装或未找到")
        print("请运行: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        return False

def show_usage_info():
    """显示使用说明"""
    print("\n" + "="*60)
    print("🎯 Olist E-commerce BI Dashboard")
    print("="*60)
    print("📊 功能特色:")
    print("   • 5个分析模块：概览、分级、地理、性能、洞察")
    print("   • 实时交互式筛选和KPI更新")
    print("   • 专业级可视化图表")
    print("   • 移动端适配设计")
    print("\n🔧 技术栈:")
    print("   • Streamlit + Plotly + Pandas")
    print("   • 机器学习卖家分级算法")
    print("   • 响应式Web设计")
    print("\n📁 项目结构:")
    print("   • src/          - 核心分析模块")
    print("   • dashboard/    - Web应用")
    print("   • data/         - 数据文件")
    print("   • reports/      - 分析报告")
    print("="*60)

def main():
    """主函数"""
    show_usage_info()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查数据文件
    check_data_files()
    
    # 启动Dashboard
    success = run_dashboard()
    
    if success:
        print("\n✅ Dashboard运行完成")
    else:
        print("\n❌ Dashboard启动失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 