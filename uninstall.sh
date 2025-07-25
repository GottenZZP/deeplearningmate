#!/bin/bash
# DeepLearningMate 卸载脚本

set -e

echo "🗑️ DeepLearningMate 卸载程序"
echo "================================"

# 确认卸载
read -p "⚠️ 确定要完全卸载 DeepLearningMate 吗？这将删除所有相关文件和配置 (y/N): " confirm
case "$confirm" in
    [yY]|[yY][eE][sS]) ;;
    *) echo "❌ 取消卸载"; exit 0 ;;
esac

echo "🧹 开始清理..."

# 1. 删除命令行工具符号链接
echo "🔗 删除命令行工具..."
if [ -L "/usr/local/bin/dlmate" ]; then
    sudo rm -f /usr/local/bin/dlmate
    echo "✅ 已删除 /usr/local/bin/dlmate"
fi

# 2. 删除虚拟环境
echo "🐍 删除Python虚拟环境..."
if [ -d "venv" ]; then
    rm -rf venv
    echo "✅ 已删除虚拟环境"
fi

# 3. 删除用户配置和缓存目录
echo "📁 删除用户配置和缓存..."
CONFIG_DIR="$HOME/.deeplearningmate"
if [ -d "$CONFIG_DIR" ]; then
    read -p "是否删除用户配置和缓存目录 $CONFIG_DIR？(y/N): " delete_config
    case "$delete_config" in
        [yY]|[yY][eE][sS])
            rm -rf "$CONFIG_DIR"
            echo "✅ 已删除配置目录"
            ;;
        *)
            echo "⏭️ 保留配置目录"
            ;;
    esac
fi

# 4. 清理环境变量（可选）
echo "🔧 清理环境变量..."
read -p "是否清理 .bashrc 中的 CUDA 相关环境变量？(y/N): " clean_env
case "$clean_env" in
    [yY]|[yY][eE][sS])
        # 备份 .bashrc
        cp "$HOME/.bashrc" "$HOME/.bashrc.dlmate.backup"
        
        # 删除 CUDA 相关环境变量
        sed -i '/# DeepLearningMate CUDA/d' "$HOME/.bashrc"
        sed -i '/export CUDA_HOME/d' "$HOME/.bashrc"
        sed -i '/export PATH.*cuda/d' "$HOME/.bashrc"
        sed -i '/export LD_LIBRARY_PATH.*cuda/d' "$HOME/.bashrc"
        
        echo "✅ 已清理环境变量（备份保存为 .bashrc.dlmate.backup）"
        ;;
    *)
        echo "⏭️ 保留环境变量"
        ;;
esac

# 5. 询问是否卸载已安装的CUDA
echo "🎯 CUDA 安装管理..."
read -p "是否卸载通过 DeepLearningMate 安装的 CUDA 版本？(y/N): " remove_cuda
case "$remove_cuda" in
    [yY]|[yY][eE][sS])
        echo "⚠️ 正在卸载 CUDA..."
        
        # 删除 CUDA 安装目录
        if [ -d "/usr/local/cuda" ]; then
            sudo rm -rf /usr/local/cuda
        fi
        
        # 删除其他 CUDA 版本目录
        sudo find /usr/local -maxdepth 1 -name "cuda-*" -type d -exec rm -rf {} + 2>/dev/null || true
        
        echo "✅ 已卸载 CUDA"
        ;;
    *)
        echo "⏭️ 保留 CUDA 安装"
        ;;
esac

# 6. 删除项目文件（可选）
echo "📦 项目文件管理..."
read -p "是否删除整个 DeepLearningMate 项目目录？(y/N): " remove_project
case "$remove_project" in
    [yY]|[yY][eE][sS])
        PROJECT_DIR="$(pwd)"
        cd ..
        rm -rf "$PROJECT_DIR"
        echo "✅ 已删除项目目录"
        echo "🎉 DeepLearningMate 已完全卸载！"
        exit 0
        ;;
    *)
        echo "⏭️ 保留项目文件"
        ;;
esac

echo "🎉 DeepLearningMate 卸载完成！"
echo ""
echo "📋 卸载总结:"
echo "  ✅ 命令行工具已删除"
echo "  ✅ 虚拟环境已删除"
echo "  📁 项目文件已保留"
echo ""
echo "💡 如需完全删除，请手动删除项目目录"