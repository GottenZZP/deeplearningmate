import subprocess
import sys
from typing import Optional

class FrameworkInstaller:
    def __init__(self):
        self.pytorch_versions = {
            '11.8': 'torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118',
            '12.0': 'torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121',
            '12.1': 'torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121'
        }
        
        self.tensorflow_versions = {
            '11.8': 'tensorflow[and-cuda]',
            '12.0': 'tensorflow[and-cuda]',
            '12.1': 'tensorflow[and-cuda]'
        }
    
    def install_pytorch(self, cuda_version: str, mirror: str = 'official') -> bool:
        """安装PyTorch"""
        if cuda_version not in self.pytorch_versions:
            print(f"❌ 不支持的CUDA版本: {cuda_version}")
            return False
        
        cmd = f"pip install {self.pytorch_versions[cuda_version]}"
        if mirror == 'china':
            cmd += " -i https://pypi.tuna.tsinghua.edu.cn/simple"
        
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ PyTorch安装失败: {e}")
            return False
    
    def install_tensorflow(self, cuda_version: str, mirror: str = 'official') -> bool:
        """安装TensorFlow"""
        if cuda_version not in self.tensorflow_versions:
            print(f"❌ 不支持的CUDA版本: {cuda_version}")
            return False
        
        cmd = f"pip install {self.tensorflow_versions[cuda_version]}"
        if mirror == 'china':
            cmd += " -i https://pypi.tuna.tsinghua.edu.cn/simple"
        
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ TensorFlow安装失败: {e}")
            return False