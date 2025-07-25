import click
import sys
from pathlib import Path
from .version_manager import CudaVersionManager
from .version_detector import CudaVersionDetector
from .transaction_manager import TransactionManager

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """🚀 DeepLearningMate - 深度学习环境管理工具"""
    pass

@cli.command()
def status():
    """显示当前环境状态"""
    detector = CudaVersionDetector()
    current = detector.get_current_cuda_version()
    installed = detector.get_installed_cuda_versions()
    
    click.echo("📊 当前环境状态")
    click.echo("=" * 30)
    click.echo(f"当前CUDA版本: {click.style(current or '未安装', fg='green' if current else 'red')}")
    
    if installed:
        click.echo(f"已安装版本: {', '.join(installed)}")
    else:
        click.echo("已安装版本: 无")
    
    # 检查GPU
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            click.echo("GPU驱动: ✅ 正常")
        else:
            click.echo("GPU驱动: ❌ 异常")
    except FileNotFoundError:
        click.echo("GPU驱动: ❌ 未安装")

@cli.command()
@click.argument('version')
@click.option('--framework', type=click.Choice(['pytorch', 'tensorflow', 'both']), 
              help='同时安装深度学习框架')
@click.option('--mirror', type=click.Choice(['official', 'china']), default='official',
              help='下载镜像源')
def install(version, framework, mirror):
    """安装指定版本的CUDA环境"""
    click.echo(f"🚀 开始安装CUDA {version}")
    
    if framework:
        click.echo(f"📦 将同时安装: {framework}")
    
    manager = CudaVersionManager()
    
    # 设置镜像源 - 需要实现具体逻辑
    if mirror == 'china':
        click.echo("🇨🇳 使用国内镜像源")
        # 设置下载器使用国内镜像源
        _configure_china_mirror()
    
    try:
        if manager.install_cuda_version(version):
            click.echo(f"✅ CUDA {version} 安装成功")
            
            # 实现框架安装逻辑
            if framework:
                success = _install_frameworks(framework, version, mirror)
                if success:
                    click.echo(f"✅ {framework} 安装成功")
                else:
                    click.echo(f"❌ {framework} 安装失败")
                
        else:
            click.echo(f"❌ CUDA {version} 安装失败")
            
    except KeyboardInterrupt:
        click.echo("\n⚠️ 安装被用户中断")
    except Exception as e:
        click.echo(f"❌ 安装过程中发生错误: {e}")

def _configure_china_mirror():
    """配置国内镜像源"""
    # 可以在这里修改下载器的URL配置
    pass

def _install_frameworks(framework, cuda_version, mirror):
    """安装深度学习框架的辅助函数"""
    from .framework_installer import FrameworkInstaller
    installer = FrameworkInstaller()
    
    if framework == 'pytorch':
        return installer.install_pytorch(cuda_version, mirror)
    elif framework == 'tensorflow':
        return installer.install_tensorflow(cuda_version, mirror)
    elif framework == 'both':
        pytorch_success = installer.install_pytorch(cuda_version, mirror)
        tensorflow_success = installer.install_tensorflow(cuda_version, mirror)
        return pytorch_success and tensorflow_success
    
    return False

@cli.command()
def interactive():
    """交互式安装向导"""
    click.echo("🧙‍♂️ DeepLearningMate 安装向导")
    click.echo("=" * 35)
    
    # 检测系统
    detector = CudaVersionDetector()
    current = detector.get_current_cuda_version()
    
    if current:
        click.echo(f"检测到当前CUDA版本: {current}")
        if not click.confirm('是否要更换版本？'):
            return
    
    # 选择用途
    click.echo("\n请选择您的使用场景:")
    use_cases = {
        '1': '学习和实验',
        '2': '研究和开发', 
        '3': '生产环境',
        '4': '游戏和娱乐'
    }
    
    for key, value in use_cases.items():
        click.echo(f"  {key}. {value}")
    
    use_case = click.prompt('请选择', type=click.Choice(list(use_cases.keys())))
    
    # 选择框架
    click.echo("\n请选择深度学习框架:")
    frameworks = {
        '1': 'PyTorch',
        '2': 'TensorFlow',
        '3': '两者都要',
        '4': '暂不安装'
    }
    
    for key, value in frameworks.items():
        click.echo(f"  {key}. {value}")
    
    framework = click.prompt('请选择', type=click.Choice(list(frameworks.keys())))
    
    # 推荐配置
    recommended_version = _get_recommended_version(use_case, framework)
    
    click.echo(f"\n📋 推荐配置:")
    click.echo(f"  CUDA版本: {recommended_version}")
    click.echo(f"  使用场景: {use_cases[use_case]}")
    click.echo(f"  深度学习框架: {frameworks[framework]}")
    
    # 在 interactive 命令的最后
    if click.confirm('\n确认安装此配置？'):
        # 执行安装
        ctx = click.get_current_context()
        
        # 将数字选择转换为实际的框架名称
        framework_mapping = {
            '1': 'pytorch',
            '2': 'tensorflow', 
            '3': 'both',
            '4': None
        }
        
        selected_framework = framework_mapping.get(framework)
        
        ctx.invoke(install, version=recommended_version, 
                  framework=selected_framework, mirror='official')

def _get_recommended_version(use_case, framework):
    """根据使用场景推荐CUDA版本"""
    # 简单的推荐逻辑
    if use_case in ['1', '2']:  # 学习和研究
        return '11.8'  # 稳定版本
    else:  # 生产环境
        return '12.0'  # 最新稳定版

@cli.command()
@click.option('--force', is_flag=True, help='强制卸载，不询问确认')
@click.option('--keep-config', is_flag=True, help='保留配置文件')
@click.option('--keep-cuda', is_flag=True, help='保留CUDA安装')
def uninstall(force, keep_config, keep_cuda):
    """卸载 DeepLearningMate"""
    click.echo("🗑️ DeepLearningMate 卸载程序")
    click.echo("=" * 35)
    
    if not force:
        if not click.confirm('⚠️ 确定要卸载 DeepLearningMate 吗？'):
            click.echo("❌ 取消卸载")
            return
    
    # 在 uninstall 命令中
    try:
        # 1. 停止监控服务（如果正在运行）
        click.echo("🛑 停止服务...")
        _stop_monitoring_service()
        
        # 2. 清理缓存和临时文件
        click.echo("🧹 清理缓存...")
        manager = CudaVersionManager()
        cache_dir = Path.home() / '.deeplearningmate'
        
        if cache_dir.exists() and not keep_config:
            import shutil
            shutil.rmtree(cache_dir)
            click.echo("✅ 已删除配置和缓存")
        
        # 3. 卸载CUDA（可选）
        if not keep_cuda:
            if click.confirm('是否卸载通过 DeepLearningMate 安装的 CUDA？'):
                click.echo("🎯 卸载 CUDA...")
                # 调用CUDA卸载逻辑
                _uninstall_cuda()
        
        # 4. 清理环境变量
        click.echo("🔧 清理环境变量...")
        _cleanup_environment()
        
        click.echo("✅ DeepLearningMate 卸载完成！")
        click.echo("")
        click.echo("💡 要完全删除，请运行: ./uninstall.sh")
        
    except Exception as e:
        click.echo(f"❌ 卸载过程中发生错误: {e}")
        click.echo("💡 请尝试运行: ./uninstall.sh")

@cli.command()
def cleanup():
    """清理缓存和临时文件"""
    click.echo("🧹 清理缓存和临时文件...")
    
    cache_dir = Path.home() / '.deeplearningmate' / 'cuda_cache'
    temp_dir = Path.home() / '.deeplearningmate' / 'temp'
    
    total_size = 0
    
    # 计算缓存大小
    if cache_dir.exists():
        for file_path in cache_dir.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    
    if total_size > 0:
        size_mb = total_size / (1024 * 1024)
        click.echo(f"📊 缓存大小: {size_mb:.1f} MB")
        
        if click.confirm('确定要清理缓存吗？'):
            import shutil
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)
            
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            click.echo("✅ 缓存清理完成")
    else:
        click.echo("✅ 缓存已经是空的")

def _uninstall_cuda():
    """卸载CUDA的内部函数"""
    cuda_paths = ['/usr/local/cuda', '/usr/local/cuda-*']
    
    for cuda_path in cuda_paths:
        if '*' in cuda_path:
            import glob
            for path in glob.glob(cuda_path):
                if Path(path).exists():
                    import shutil
                    shutil.rmtree(path)
                    print(f"✅ 已删除: {path}")
        else:
            if Path(cuda_path).exists():
                import shutil
                if Path(cuda_path).is_symlink():
                    Path(cuda_path).unlink()
                else:
                    shutil.rmtree(cuda_path)
                print(f"✅ 已删除: {cuda_path}")

def _cleanup_environment():
    """清理环境变量的内部函数"""
    bashrc_path = Path.home() / '.bashrc'
    
    if bashrc_path.exists():
        # 读取当前内容
        with open(bashrc_path, 'r') as f:
            lines = f.readlines()
        
        # 过滤掉CUDA相关的行
        filtered_lines = []
        for line in lines:
            if not any(keyword in line for keyword in 
                      ['CUDA_HOME', 'cuda/bin', 'cuda/lib', '# DeepLearningMate']):
                filtered_lines.append(line)
        
        # 写回文件
        with open(bashrc_path, 'w') as f:
            f.writelines(filtered_lines)
        
        print("✅ 已清理环境变量")

# 在文件末尾添加以下命令

@cli.command('list-versions')
def list_versions():
    """列出所有可用的CUDA版本"""
    manager = CudaVersionManager()
    available = manager.list_available_versions()
    installed = manager.list_installed_versions()
    
    click.echo("📋 CUDA版本列表")
    click.echo("=" * 30)
    
    for version in available:
        status = "✅ 已安装" if version in installed else "⬜ 未安装"
        click.echo(f"  {version} - {status}")

@cli.command()
@click.argument('version')
def switch(version):
    """切换到指定的CUDA版本"""
    manager = CudaVersionManager()
    
    with manager.transaction_manager.transaction() as tx:
        if manager._do_switch_cuda_version(version, tx):
            click.echo(f"✅ 成功切换到CUDA {version}")
        else:
            click.echo(f"❌ 切换到CUDA {version}失败")

@cli.command()
def recover():
    """自动恢复到最近的稳定状态"""
    from .monitor import SystemMonitor
    monitor = SystemMonitor()
    monitor._auto_recover()
    click.echo("🔄 自动恢复完成")

@cli.command('install-framework')
@click.argument('framework', type=click.Choice(['pytorch', 'tensorflow']))
@click.option('--cuda-version', help='指定CUDA版本')
@click.option('--mirror', type=click.Choice(['official', 'china']), default='official')
def install_framework(framework, cuda_version, mirror):
    """安装深度学习框架"""
    from .framework_installer import FrameworkInstaller
    
    if not cuda_version:
        detector = CudaVersionDetector()
        cuda_version = detector.get_current_cuda_version()
        if not cuda_version:
            click.echo("❌ 未检测到CUDA版本，请先安装CUDA")
            return
    
    installer = FrameworkInstaller()
    
    if framework == 'pytorch':
        success = installer.install_pytorch(cuda_version, mirror)
    else:
        success = installer.install_tensorflow(cuda_version, mirror)
    
    if success:
        click.echo(f"✅ {framework} 安装成功")
    else:
        click.echo(f"❌ {framework} 安装失败")

@cli.command('install-stack')
@click.argument('framework', type=click.Choice(['pytorch', 'tensorflow']))
@click.argument('cuda_version')
@click.option('--mirror', type=click.Choice(['official', 'china']), default='official')
def install_stack(framework, cuda_version, mirror):
    """安装完整深度学习环境（CUDA + cuDNN + 框架）"""
    manager = CudaVersionManager()
    
    # 1. 安装CUDA
    click.echo(f"🚀 安装CUDA {cuda_version}...")
    if not manager.install_cuda_version(cuda_version):
        click.echo("❌ CUDA安装失败")
        return
    
    # 2. 安装框架
    click.echo(f"📦 安装{framework}...")
    ctx = click.get_current_context()
    ctx.invoke(install_framework, framework=framework, cuda_version=cuda_version, mirror=mirror)

@cli.command()
@click.argument('name')
def checkpoint(name):
    """创建系统检查点"""
    from .rollback import RollbackManager
    manager = RollbackManager()
    manager.create_checkpoint(name)
    click.echo(f"✅ 检查点 '{name}' 创建成功")

@cli.command()
@click.argument('name')
def rollback(name):
    """回滚到指定检查点"""
    from .rollback import RollbackManager
    manager = RollbackManager()
    try:
        manager.rollback_to_checkpoint(name)
        click.echo(f"✅ 成功回滚到检查点 '{name}'")
    except FileNotFoundError:
        click.echo(f"❌ 检查点 '{name}' 不存在")

# 将_stop_monitoring_service函数移动到第447行之前
def _stop_monitoring_service():
    """停止监控服务"""
    try:
        import psutil
        # 查找并停止监控进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'deeplearningmate' in ' '.join(proc.info['cmdline'] or []):
                proc.terminate()
                click.echo(f"✅ 已停止监控进程 PID: {proc.info['pid']}")
    except Exception as e:
        click.echo(f"⚠️ 停止监控服务时出错: {e}")

if __name__ == '__main__':
    cli()