import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from .transaction_manager import TransactionManager
from .downloader import CudaDownloader
from .version_detector import CudaVersionDetector

class CudaVersionManager:
    def __init__(self):
        self.cache_dir = Path.home() / '.deeplearningmate' / 'cuda_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.install_base = Path('/usr/local')
        self.transaction_manager = TransactionManager()
        self.detector = CudaVersionDetector()
    
    def install_cuda_version(self, version: str) -> bool:
        """安装指定版本的CUDA（公共接口）"""
        return self.switch_cuda_version(version)
    
    def switch_cuda_version(self, target_version: str) -> bool:
        """安全地切换CUDA版本"""
        with self.transaction_manager.transaction(f"switch_cuda_{target_version}") as tx:
            return self._do_switch_cuda_version(target_version, tx)
    
    def _do_switch_cuda_version(self, target_version: str, tx) -> bool:
        """执行CUDA版本切换"""
        print(f"🔄 准备切换到CUDA {target_version}...")
        
        # 添加自定义回滚操作
        current_version = self._get_current_version()
        if current_version:
            tx.add_rollback_action({
                'type': 'restore_cuda_version',
                'version': current_version
            })
        
        # 1. 检查目标版本是否已安装
        if self._is_version_installed(target_version):
            print(f"✅ 检测到CUDA {target_version}已安装")
            return self._activate_version(target_version)
        
        # 2. 检查缓存中是否有该版本
        if self._is_version_cached(target_version):
            print(f"📦 从缓存恢复CUDA {target_version}...")
            return self._restore_from_cache(target_version)
        
        # 3. 下载并安装新版本
        print(f"⬇️ 下载CUDA {target_version}...")
        if self._download_and_install(target_version, tx):
            return self._activate_version(target_version)
        
        return False
    
    def _download_and_install(self, version: str, tx) -> bool:
        """下载并安装CUDA"""
        try:
            # 检测Ubuntu版本
            ubuntu_version = self._detect_ubuntu_version()
            
            # 下载过程中的检查点
            downloader = CudaDownloader()
            installer_path = downloader.download_cuda(version, ubuntu_version, 
                                                    Path("/tmp"))
            
            if not installer_path:
                return False
            
            # 添加清理下载文件的回滚操作
            tx.add_rollback_action({
                'type': 'cleanup_file',
                'path': str(installer_path)
            })
            
            # 执行安装
            return self._install_cuda_package(installer_path, version, tx)
            
        except Exception as e:
            print(f"❌ 下载安装失败: {e}")
            return False
    
    def _install_cuda_package(self, installer_path: Path, version: str, tx) -> bool:
        """执行CUDA安装包的安装"""
        try:
            print(f"🔧 安装CUDA {version}...")
            
            # 设置安装目录
            install_dir = self.install_base / f'cuda-{version}'
            
            # 添加回滚操作：删除安装目录
            tx.add_rollback_action({
                'type': 'remove_directory',
                'path': str(install_dir)
            })
            
            # 执行静默安装
            cmd = [
                'sudo', 'sh', str(installer_path),
                '--silent',
                '--toolkit',
                f'--toolkitpath={install_dir}',
                '--no-opengl-libs'  # 避免与系统OpenGL库冲突
            ]
            
            print(f"🚀 执行安装命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ CUDA {version} 安装成功")
                return True
            else:
                print(f"❌ CUDA安装失败:")
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 安装过程中发生错误: {e}")
            return False
    
    def _detect_ubuntu_version(self) -> str:
        """检测Ubuntu版本"""
        try:
            result = subprocess.run(['lsb_release', '-rs'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                # 映射到支持的版本
                if version.startswith('20.'):
                    return 'ubuntu20'
                elif version.startswith('22.'):
                    return 'ubuntu22'
                else:
                    print(f"⚠️ 未明确支持的Ubuntu版本 {version}，使用ubuntu22")
                    return 'ubuntu22'
        except Exception as e:
            print(f"⚠️ 检测Ubuntu版本失败: {e}，使用默认ubuntu22")
            return 'ubuntu22'
    
    def _get_current_version(self) -> Optional[str]:
        """获取当前激活的CUDA版本"""
        return self.detector.get_current_cuda_version()
    
    def _is_version_installed(self, version: str) -> bool:
        """检查版本是否已安装"""
        cuda_path = self.install_base / f'cuda-{version}'
        return cuda_path.exists() and (cuda_path / 'bin' / 'nvcc').exists()
    
    def _is_version_cached(self, version: str) -> bool:
        """检查版本是否在缓存中"""
        cache_path = self.cache_dir / f'cuda-{version}'
        return cache_path.exists()
    
    def _activate_version(self, version: str) -> bool:
        """激活指定版本的CUDA"""
        try:
            # 备份当前版本到缓存
            current_version = self._get_current_version()
            if current_version and current_version != version:
                self._backup_to_cache(current_version)
            
            # 更新软链接
            cuda_link = self.install_base / 'cuda'
            cuda_target = self.install_base / f'cuda-{version}'
            
            if cuda_link.is_symlink():
                cuda_link.unlink()
            elif cuda_link.exists():
                # 如果是目录，先备份
                shutil.move(str(cuda_link), str(cuda_link) + '.backup')
            
            cuda_link.symlink_to(cuda_target)
            
            # 更新环境变量
            self._update_environment(version)
            
            print(f"✅ 成功切换到CUDA {version}")
            return True
            
        except Exception as e:
            print(f"❌ 切换失败: {e}")
            return False
    
    def _update_environment(self, version: str):
        """更新环境变量"""
        try:
            cuda_home = self.install_base / f'cuda-{version}'
            
            # 更新当前会话的环境变量
            os.environ['CUDA_HOME'] = str(cuda_home)
            os.environ['CUDA_ROOT'] = str(cuda_home)
            
            # 更新PATH
            cuda_bin = str(cuda_home / 'bin')
            current_path = os.environ.get('PATH', '')
            if cuda_bin not in current_path:
                os.environ['PATH'] = f"{cuda_bin}:{current_path}"
            
            # 更新LD_LIBRARY_PATH
            cuda_lib = str(cuda_home / 'lib64')
            current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
            if cuda_lib not in current_ld_path:
                os.environ['LD_LIBRARY_PATH'] = f"{cuda_lib}:{current_ld_path}"
            
            # 持久化到.bashrc
            self._update_bashrc(version)
            
            print(f"🔧 环境变量已更新为CUDA {version}")
            
        except Exception as e:
            print(f"⚠️ 更新环境变量失败: {e}")
    
    def _update_bashrc(self, version: str):
        """更新.bashrc文件"""
        try:
            bashrc_path = Path.home() / '.bashrc'
            cuda_home = self.install_base / f'cuda-{version}'
            
            # 读取现有内容
            if bashrc_path.exists():
                with open(bashrc_path, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # 移除旧的CUDA配置
            filtered_lines = []
            for line in lines:
                if not any(keyword in line for keyword in 
                          ['CUDA_HOME', 'cuda/bin', 'cuda/lib', '# DeepLearningMate']):
                    filtered_lines.append(line)
            
            # 添加新的CUDA配置
            cuda_config = [
                '\n# DeepLearningMate CUDA Configuration\n',
                f'export CUDA_HOME={cuda_home}\n',
                f'export CUDA_ROOT={cuda_home}\n',
                f'export PATH={cuda_home}/bin:$PATH\n',
                f'export LD_LIBRARY_PATH={cuda_home}/lib64:$LD_LIBRARY_PATH\n'
            ]
            
            # 写回文件
            with open(bashrc_path, 'w') as f:
                f.writelines(filtered_lines + cuda_config)
            
            print(f"📝 已更新 {bashrc_path}")
            
        except Exception as e:
            print(f"⚠️ 更新.bashrc失败: {e}")
    
    def _backup_to_cache(self, version: str):
        """备份版本到缓存"""
        source = self.install_base / f'cuda-{version}'
        target = self.cache_dir / f'cuda-{version}'
        
        if source.exists() and not target.exists():
            print(f"💾 备份CUDA {version}到缓存...")
            shutil.copytree(source, target)
    
    def _restore_from_cache(self, version: str) -> bool:
        """从缓存恢复版本"""
        try:
            source = self.cache_dir / f'cuda-{version}'
            target = self.install_base / f'cuda-{version}'
            
            if target.exists():
                shutil.rmtree(target)
            
            shutil.copytree(source, target)
            return self._activate_version(version)
            
        except Exception as e:
            print(f"❌ 从缓存恢复失败: {e}")
            return False
    
    def list_available_versions(self) -> List[str]:
        """列出所有可用的CUDA版本"""
        downloader = CudaDownloader()
        return list(downloader.download_urls.keys())
    
    def list_installed_versions(self) -> List[str]:
        """列出已安装的CUDA版本"""
        return self.detector.get_installed_cuda_versions()
    
    def uninstall_version(self, version: str) -> bool:
        """卸载指定版本的CUDA"""
        try:
            cuda_path = self.install_base / f'cuda-{version}'
            cache_path = self.cache_dir / f'cuda-{version}'
            
            # 检查是否为当前激活版本
            current = self._get_current_version()
            if current == version:
                print(f"⚠️ CUDA {version} 是当前激活版本，无法卸载")
                return False
            
            # 删除安装目录
            if cuda_path.exists():
                shutil.rmtree(cuda_path)
                print(f"✅ 已删除安装目录: {cuda_path}")
            
            # 删除缓存
            if cache_path.exists():
                shutil.rmtree(cache_path)
                print(f"✅ 已删除缓存: {cache_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ 卸载失败: {e}")
            return False