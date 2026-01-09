"""用户模型"""
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime


class User:
    """用户类"""
    
    def __init__(self, user_id: str, username: str, email: str, password_hash: str, created_at: str = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """从字典创建用户"""
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            created_at=data.get('created_at')
        )


class UserManager:
    """用户管理器"""
    
    def __init__(self, db_path: str = "./data/users.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_users()
    
    def _load_users(self):
        """加载用户数据"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = {user_id: User.from_dict(user_data) 
                                 for user_id, user_data in data.items()}
            except Exception as e:
                print(f"加载用户数据失败: {e}")
                self.users = {}
        else:
            self.users = {}
    
    def _save_users(self):
        """保存用户数据"""
        try:
            data = {user_id: user.to_dict() 
                   for user_id, user in self.users.items()}
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存用户数据失败: {e}")
            return False
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username: str, email: str, password: str) -> tuple[Optional[User], Optional[str]]:
        """
        注册新用户
        
        Returns:
            (User, None) 成功
            (None, error_message) 失败
        """
        # 检查用户名是否已存在
        for user in self.users.values():
            if user.username == username:
                return None, "用户名已存在"
            if user.email == email:
                return None, "邮箱已被注册"
        
        # 创建新用户
        import uuid
        user_id = str(uuid.uuid4())
        password_hash = self._hash_password(password)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        self.users[user_id] = user
        
        if self._save_users():
            return user, None
        else:
            return None, "注册失败，无法保存用户数据"
    
    def login(self, username: str, password: str) -> tuple[Optional[User], Optional[str]]:
        """
        用户登录
        
        Returns:
            (User, None) 成功
            (None, error_message) 失败
        """
        # 查找用户
        user = None
        for u in self.users.values():
            if u.username == username or u.email == username:
                user = u
                break
        
        if not user:
            return None, "用户名或密码错误"
        
        # 验证密码
        password_hash = self._hash_password(password)
        if user.password_hash != password_hash:
            return None, "用户名或密码错误"
        
        return user, None
    
    def get_user(self, user_id: str) -> Optional[User]:
        """根据用户ID获取用户"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None


# 全局用户管理器实例
user_manager = UserManager()

