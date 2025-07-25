import psutil
import time
import subprocess
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .transaction_manager import TransactionManager

class CudaChangeHandler(FileSystemEventHandler):
    def __init__(self, monitor):
        self.monitor = monitor
    
    def on_modified(self, event):
        if 'cuda' in event.src_path.lower():
            print(f"🔍 检测到CUDA目录变化: {event.src_path}")
            self.monitor._check_system_health()

class SystemMonitor:
    def __init__(self):
        self.transaction_manager = TransactionManager()
        self.monitoring = False
    
    def start_monitoring(self):
        """开始监控系统状态"""
        self.monitoring = True
        
        # 监控CUDA目录变化
        observer = Observer()
        observer.schedule(CudaChangeHandler(self), '/usr/local', recursive=True)
        observer.start()
        
        try:
            while self.monitoring:
                self._check_system_health()
                time.sleep(30)  # 每30秒检查一次
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    
    def _check_system_health(self):
        """检查系统健康状态"""
        # 检查CUDA是否正常
        try:
            result = subprocess.run(['nvcc', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("⚠️ 检测到CUDA异常，尝试自动恢复...")
                self._auto_recover()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️ CUDA命令无响应，尝试自动恢复...")
            self._auto_recover()
    
    def _auto_recover(self):
        """自动恢复"""
        # 查找最近的成功备份
        backup_files = list(self.transaction_manager.backup_dir.glob('*.json'))
        for backup_file in sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True):
            with open(backup_file) as f:
                backup_data = json.load(f)
            
            if backup_data.get('status') == 'committed':
                print(f"🔄 恢复到备份: {backup_data['operation']}")
                self.transaction_manager._rollback_transaction(backup_data['id'])
                break