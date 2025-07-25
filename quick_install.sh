#!/bin/bash
# 一键安装脚本 - 用户直接运行

set -e

echo "🚀 DeepLearningMate 一键安装"
echo "============================"

# 检查网络连接
if ! ping -c 1 github.com &> /dev/null; then
    echo "❌ 网络连接失败，请检查网络设置"
    exit 1
fi

# 下载项目
echo "📥 下载DeepLearningMate..."
if [ -d "deeplearningmate" ]; then
    echo "⚠️ 目录已存在，正在更新..."
    cd deeplearningmate
    git pull
else
    git clone https://github.com/yourusername/deeplearningmate.git
    cd deeplearningmate
fi

# 运行安装
echo "🔧 开始安装..."
./install.sh

echo "🎉 安装完成！"
echo ""
echo "快速开始:"
echo "  dlmate status          # 查看当前状态"
echo "  dlmate interactive     # 交互式安装向导"
echo "  dlmate install 12.0    # 直接安装CUDA 12.0"