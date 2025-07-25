#!/bin/bash
# DeepLearningMate 安装脚本

set -e

echo "🚀 DeepLearningMate 安装程序"
echo "================================"

# 检查系统 - 修复兼容性问题
case "$OSTYPE" in
  linux-gnu*) ;;
  *) echo "❌ 此工具仅支持Linux系统"; exit 1 ;;
esac

# 检查Ubuntu版本
if ! command -v lsb_release >/dev/null 2>&1; then
    echo "❌ 无法检测Ubuntu版本"
    echo "请先安装 lsb-release: sudo apt install lsb-release"
    exit 1
fi

UBUNTU_VERSION=$(lsb_release -rs)
echo "✅ 检测到Ubuntu $UBUNTU_VERSION"

# 安装依赖
echo "📦 安装系统依赖..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv curl wget

# 创建虚拟环境
echo "🐍 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# 安装Python依赖
echo "📚 安装Python依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建符号链接
echo "🔗 创建命令行工具..."
sudo ln -sf "$(pwd)/dlmate" /usr/local/bin/dlmate
sudo chmod +x /usr/local/bin/dlmate

echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "  dlmate --help          # 查看帮助"
echo "  dlmate list-versions   # 查看可用版本"
echo "  dlmate switch 12.0     # 切换到CUDA 12.0"
echo ""
echo "首次使用建议:"
echo "  dlmate install 12.0    # 安装CUDA 12.0"