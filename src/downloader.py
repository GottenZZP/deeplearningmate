import requests
import os
from pathlib import Path
from typing import Dict, Optional
from tqdm import tqdm

class CudaDownloader:
    def __init__(self, use_china_mirror=False):
        # 原有的官方下载链接
        self.download_urls = {
            '11.8': {
                'ubuntu20': 'https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run',
                'ubuntu22': 'https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run'
            },
            '12.0': {
                'ubuntu20': 'https://developer.download.nvidia.com/compute/cuda/12.0.0/local_installers/cuda_12.0.0_525.60.13_linux.run',
                'ubuntu22': 'https://developer.download.nvidia.com/compute/cuda/12.0.0/local_installers/cuda_12.0.0_525.60.13_linux.run'
            },
            '12.1': {
                'ubuntu20': 'https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run',
                'ubuntu22': 'https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run'
            }
        }
        
        # 国内镜像源链接
        self.china_mirror_urls = {
            '11.8': {
                'ubuntu20': 'https://mirrors.tuna.tsinghua.edu.cn/nvidia/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run',
                'ubuntu22': 'https://mirrors.tuna.tsinghua.edu.cn/nvidia/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run'
            },
            '12.0': {
                'ubuntu20': 'https://mirrors.tuna.tsinghua.edu.cn/nvidia/cuda/12.0.0/local_installers/cuda_12.0.0_525.60.13_linux.run',
                'ubuntu22': 'https://mirrors.tuna.tsinghua.edu.cn/nvidia/cuda/12.0.0/local_installers/cuda_12.0.0_525.60.13_linux.run'
            },
            '12.1': {
                'ubuntu20': 'https://mirrors.tuna.tsinghua.edu.cn/nvidia/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run',
                'ubuntu22': 'https://mirrors.tuna.tsinghua.edu.cn/nvidia/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run'
            }
        }
        
        # 根据参数选择使用的URL
        if use_china_mirror:
            self.current_urls = self.china_mirror_urls
        else:
            self.current_urls = self.download_urls
    
    def download_cuda(self, version: str, ubuntu_version: str, download_dir: Path) -> Optional[Path]:
        """下载CUDA安装包"""
        if version not in self.current_urls:
            print(f"❌ 不支持的CUDA版本: {version}")
            return None
        
        url = self.current_urls[version].get(ubuntu_version)
        if not url:
            print(f"❌ 不支持的Ubuntu版本: {ubuntu_version}")
            return None
        
        filename = url.split('/')[-1]
        filepath = download_dir / filename
        
        if filepath.exists():
            print(f"✅ 安装包已存在: {filepath}")
            return filepath
        
        print(f"⬇️ 下载CUDA {version}...")
        return self._download_file(url, filepath)
    
    def _download_file(self, url: str, filepath: Path) -> Optional[Path]:
        """下载文件并显示进度"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f, tqdm(
                desc=filepath.name,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
            
            print(f"✅ 下载完成: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            if filepath.exists():
                filepath.unlink()
            return None