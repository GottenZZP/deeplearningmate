# DeepLearningMate 🚀

一键安装和管理深度学习CUDA环境的工具，专为Ubuntu系统设计。

## ✨ 特性

- 🎯 **一键安装**: 自动下载和安装CUDA、cuDNN
- 🔄 **版本切换**: 快速切换不同CUDA版本
- 🛡️ **安全回滚**: 操作失败自动恢复
- 📦 **智能缓存**: 避免重复下载
- 🔍 **兼容检测**: 自动检测最佳版本组合
- 📊 **进度显示**: 实时显示安装进度

## 🚀 快速开始

### 一键安装

```bash
# 下载并安装
git clone https://github.com/yourusername/deeplearningmate.git
cd deeplearningmate
./install.sh
```

### 基本使用

```bash
# 查看帮助
dlmate --help

# 查看当前状态
dlmate status

# 安装CUDA 12.0
dlmate install 12.0

# 切换到CUDA 11.8
dlmate switch 11.8

# 列出所有版本
dlmate list-versions

# 卸载指定版本
dlmate uninstall 11.8
```

## 📋 支持的版本

| CUDA版本 | cuDNN版本 | PyTorch | TensorFlow | 状态 |
|----------|-----------|---------|------------|------|
| 11.8     | 8.6-8.8   | 1.13+   | 2.11+      | ✅   |
| 12.0     | 8.8-8.9   | 2.0+    | 2.13+      | ✅   |
| 12.1     | 8.9       | 2.1+    | 2.14+      | ✅   |
| 12.2     | 8.9       | 2.1+    | 2.15+      | 🚧   |

## 🛠️ 高级功能

### 环境管理

```bash
# 创建检查点
dlmate checkpoint create "before-upgrade"

# 回滚到检查点
dlmate rollback "before-upgrade"

# 清理缓存
dlmate cleanup
```

### 框架安装

```bash
# 安装PyTorch
dlmate install-framework pytorch

# 安装TensorFlow
dlmate install-framework tensorflow

# 安装完整深度学习环境
dlmate install-stack pytorch  # 包含CUDA + cuDNN + PyTorch
```

## 🔧 故障排除

### 常见问题

1. **权限错误**
   ```bash
   sudo dlmate install 12.0
   ```

2. **网络问题**
   ```bash
   dlmate install 12.0 --mirror china  # 使用国内镜像
   ```

3. **空间不足**
   ```bash
   dlmate cleanup  # 清理缓存
   ```

4. **安装失败**
   ```bash
   dlmate recover  # 自动恢复
   ```

## 📞 支持

- 📖 [文档](https://github.com/GottenZZP/deeplearningmate/wiki)
- 🐛 [问题反馈](https://github.com/GottenZZP/deeplearningmate/issues)
- 💬 [讨论区](https://github.com/GottenZZP/deeplearningmate/discussions)

## 📊 项目统计

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/GottenZZP/deeplearningmate?style=for-the-badge&logo=github)
![GitHub forks](https://img.shields.io/github/forks/GottenZZP/deeplearningmate?style=for-the-badge&logo=github)
![GitHub issues](https://img.shields.io/github/issues/GottenZZP/deeplearningmate?style=for-the-badge&logo=github)
![GitHub license](https://img.shields.io/github/license/GottenZZP/deeplearningmate?style=for-the-badge)

</div>

### ⭐ Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=GottenZZP/deeplearningmate&type=Date)](https://star-history.com/#GottenZZP/deeplearningmate&Date)

</div>

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐ Star！**

</div>