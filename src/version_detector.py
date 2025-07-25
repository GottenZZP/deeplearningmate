import subprocess
import os
import re
from typing import Optional, Dict, List

class CudaVersionDetector:
    def __init__(self):
        self.cuda_paths = [
            '/usr/local/cuda',
            '/usr/local/cuda-*',
            '/opt/cuda'
        ]
    
    def get_current_cuda_version(self) -> Optional[str]:
        """检测当前激活的CUDA版本"""
        try:
            result = subprocess.run(['nvcc', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                match = re.search(r'release (\d+\.\d+)', result.stdout)
                return match.group(1) if match else None
        except FileNotFoundError:
            return None
    
    def get_installed_cuda_versions(self) -> List[str]:
        """检测系统中已安装的所有CUDA版本"""
        versions = []
        for path_pattern in self.cuda_paths:
            if '*' in path_pattern:
                import glob
                for path in glob.glob(path_pattern):
                    version = self._extract_version_from_path(path)
                    if version:
                        versions.append(version)
            elif os.path.exists(path_pattern):
                version = self._extract_version_from_path(path_pattern)
                if version:
                    versions.append(version)
        return sorted(set(versions))
    
    def _extract_version_from_path(self, path: str) -> Optional[str]:
        """从路径中提取版本号"""
        match = re.search(r'cuda-?(\d+\.\d+)', path)
        return match.group(1) if match else None