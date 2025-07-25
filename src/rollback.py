import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from .version_manager import CudaVersionManager
from .version_detector import CudaVersionDetector

class RollbackManager:
    def __init__(self):
        self.backup_dir = Path.home() / '.deeplearningmate' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_checkpoint(self, name: str):
        """创建系统检查点"""
        checkpoint = {
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'cuda_version': self._get_current_cuda(),
            'environment_vars': dict(os.environ),
            'installed_packages': self._get_pip_packages()
        }
        
        checkpoint_file = self.backup_dir / f'{name}.json'
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    
    def rollback_to_checkpoint(self, name: str):
        """回滚到指定检查点"""
        checkpoint_file = self.backup_dir / f'{name}.json'
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"检查点不存在: {name}")
        
        with open(checkpoint_file) as f:
            checkpoint = json.load(f)
        
        # 恢复CUDA版本
        target_version = checkpoint['cuda_version']
        if target_version:
            manager = CudaVersionManager()
            manager.switch_cuda_version(target_version)
    
    def _get_current_cuda(self):
        """获取当前CUDA版本"""
        detector = CudaVersionDetector()
        return detector.get_current_cuda_version()
    
    def _get_pip_packages(self):
        """获取已安装的pip包列表"""
        try:
            result = subprocess.run(['pip', 'list', '--format=freeze'], 
                                  capture_output=True, text=True)
            return result.stdout.strip().split('\n') if result.returncode == 0 else []
        except Exception:
            return []