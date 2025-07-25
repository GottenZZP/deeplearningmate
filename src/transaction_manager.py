import os
import json
import shutil
import signal
import atexit
import traceback
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List, Optional, Callable

class TransactionManager:
    def __init__(self):
        self.backup_dir = Path.home() / '.deeplearningmate' / 'transactions'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.current_transaction = None
        self.rollback_stack = []
        
        # 注册信号处理器，处理意外中断
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self._cleanup_on_exit)
    
    @contextmanager
    def transaction(self, operation_name: str):
        """事务上下文管理器"""
        transaction_id = self._create_transaction(operation_name)
        
        try:
            print(f"🔒 开始事务: {operation_name} (ID: {transaction_id})")
            yield TransactionContext(self, transaction_id)
            
            # 事务成功完成
            self._commit_transaction(transaction_id)
            print(f"✅ 事务完成: {operation_name}")
            
        except Exception as e:
            print(f"❌ 事务失败: {operation_name}")
            print(f"错误信息: {str(e)}")
            
            # 自动回滚
            self._rollback_transaction(transaction_id)
            raise
        
        finally:
            self._cleanup_transaction(transaction_id)
    
    def _create_transaction(self, operation_name: str) -> str:
        """创建新事务"""
        transaction_id = f"{operation_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        transaction_data = {
            'id': transaction_id,
            'operation': operation_name,
            'start_time': datetime.now().isoformat(),
            'status': 'active',
            'rollback_actions': [],
            'backups': {}
        }
        
        # 创建完整的系统快照
        self._create_system_snapshot(transaction_id, transaction_data)
        
        # 保存事务信息
        transaction_file = self.backup_dir / f'{transaction_id}.json'
        with open(transaction_file, 'w') as f:
            json.dump(transaction_data, f, indent=2)
        
        self.current_transaction = transaction_id
        return transaction_id
    
    def _create_system_snapshot(self, transaction_id: str, transaction_data: Dict):
        """创建完整的系统快照"""
        print("📸 创建系统快照...")
        
        snapshot_dir = self.backup_dir / transaction_id
        snapshot_dir.mkdir(exist_ok=True)
        
        # 1. 备份CUDA安装目录
        cuda_paths = ['/usr/local/cuda', '/usr/local/cuda-*']
        for cuda_path in cuda_paths:
            if '*' in cuda_path:
                import glob
                for path in glob.glob(cuda_path):
                    if Path(path).exists():
                        self._backup_directory(path, snapshot_dir / Path(path).name)
            else:
                if Path(cuda_path).exists():
                    self._backup_directory(cuda_path, snapshot_dir / 'cuda')
        
        # 2. 备份环境变量
        env_backup = {
            'PATH': os.environ.get('PATH', ''),
            'LD_LIBRARY_PATH': os.environ.get('LD_LIBRARY_PATH', ''),
            'CUDA_HOME': os.environ.get('CUDA_HOME', ''),
            'CUDA_ROOT': os.environ.get('CUDA_ROOT', '')
        }
        
        with open(snapshot_dir / 'environment.json', 'w') as f:
            json.dump(env_backup, f, indent=2)
        
        # 3. 备份关键配置文件
        config_files = [
            Path.home() / '.bashrc',
            Path.home() / '.profile',
            Path.home() / '.zshrc',
            Path('/etc/environment')
        ]
        
        config_backup_dir = snapshot_dir / 'configs'
        config_backup_dir.mkdir(exist_ok=True)
        
        for config_file in config_files:
            if config_file.exists():
                shutil.copy2(config_file, config_backup_dir / config_file.name)
        
        transaction_data['backups'] = {
            'snapshot_dir': str(snapshot_dir),
            'cuda_backed_up': True,
            'env_backed_up': True,
            'configs_backed_up': True
        }
    
    def _backup_directory(self, source: str, target: Path):
        """备份目录"""
        source_path = Path(source)
        if source_path.exists() and source_path.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source_path, target, symlinks=True)
    
    def _rollback_transaction(self, transaction_id: str):
        """回滚事务"""
        print(f"🔄 开始回滚事务: {transaction_id}")
        
        transaction_file = self.backup_dir / f'{transaction_id}.json'
        if not transaction_file.exists():
            print(f"❌ 事务文件不存在: {transaction_id}")
            return
        
        with open(transaction_file) as f:
            transaction_data = json.load(f)
        
        snapshot_dir = Path(transaction_data['backups']['snapshot_dir'])
        
        try:
            # 1. 恢复CUDA目录
            self._restore_cuda_directories(snapshot_dir)
            
            # 2. 恢复环境变量
            self._restore_environment(snapshot_dir)
            
            # 3. 恢复配置文件
            self._restore_config_files(snapshot_dir)
            
            # 4. 执行自定义回滚操作
            for action in reversed(transaction_data.get('rollback_actions', [])):
                self._execute_rollback_action(action)
            
            print(f"✅ 事务回滚完成: {transaction_id}")
            
        except Exception as e:
            print(f"❌ 回滚失败: {e}")
            print("请手动检查系统状态")
    
    def _restore_cuda_directories(self, snapshot_dir: Path):
        """恢复CUDA目录"""
        print("🔄 恢复CUDA目录...")
        
        # 删除当前CUDA安装
        cuda_paths = ['/usr/local/cuda', '/usr/local/cuda-*']
        for cuda_path in cuda_paths:
            if '*' in cuda_path:
                import glob
                for path in glob.glob(cuda_path):
                    if Path(path).exists():
                        shutil.rmtree(path)
            else:
                if Path(cuda_path).exists():
                    if Path(cuda_path).is_symlink():
                        Path(cuda_path).unlink()
                    else:
                        shutil.rmtree(cuda_path)
        
        # 恢复备份的CUDA目录
        for backup_item in snapshot_dir.iterdir():
            if backup_item.is_dir() and backup_item.name.startswith('cuda'):
                target_path = Path('/usr/local') / backup_item.name
                if backup_item.name == 'cuda':
                    target_path = Path('/usr/local/cuda')
                
                shutil.copytree(backup_item, target_path, symlinks=True)
    
    def _restore_environment(self, snapshot_dir: Path):
        """恢复环境变量"""
        print("🔄 恢复环境变量...")
        
        env_file = snapshot_dir / 'environment.json'
        if env_file.exists():
            with open(env_file) as f:
                env_backup = json.load(f)
            
            for key, value in env_backup.items():
                if value:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
    
    def _restore_config_files(self, snapshot_dir: Path):
        """恢复配置文件"""
        print("🔄 恢复配置文件...")
        
        config_backup_dir = snapshot_dir / 'configs'
        if config_backup_dir.exists():
            for config_file in config_backup_dir.iterdir():
                if config_file.name in ['.bashrc', '.profile', '.zshrc']:
                    target = Path.home() / config_file.name
                elif config_file.name == 'environment':
                    target = Path('/etc/environment')
                else:
                    continue
                
                shutil.copy2(config_file, target)
    
    def _signal_handler(self, signum, frame):
        """处理信号中断"""
        print(f"\n⚠️ 接收到信号 {signum}，正在安全退出...")
        if self.current_transaction:
            self._rollback_transaction(self.current_transaction)
        exit(1)
    
    def _cleanup_on_exit(self):
        """程序退出时的清理"""
        if self.current_transaction:
            print("⚠️ 检测到未完成的事务，正在回滚...")
            self._rollback_transaction(self.current_transaction)

class TransactionContext:
    def __init__(self, manager: TransactionManager, transaction_id: str):
        self.manager = manager
        self.transaction_id = transaction_id
    
    def add_rollback_action(self, action: Dict):
        """添加自定义回滚操作"""
        transaction_file = self.manager.backup_dir / f'{self.transaction_id}.json'
        
        with open(transaction_file) as f:
            transaction_data = json.load(f)
        
        transaction_data['rollback_actions'].append(action)
        
        with open(transaction_file, 'w') as f:
            json.dump(transaction_data, f, indent=2)