"""
Модуль реєстрації та авторизації суб'єктів
"""

import hashlib
import json
import os
from typing import Dict, Optional


class AuthenticationModule:
    """Модуль для реєстрації та авторизації користувачів"""
    
    def __init__(self, data_file: str = "data/system.json"):
        """
        Ініціалізація модуля автентифікації
        
        Args:
            data_file: Шлях до файлу з даними системи
        """
        self.data_file = data_file
        self.users: Dict[str, Dict] = {}
        self.current_user: Optional[str] = None
        self.load_data()
    
    def _hash_password(self, password: str) -> str:
        """Хешування пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_data(self):
        """Завантаження даних користувачів з файлу"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
            except (json.JSONDecodeError, IOError):
                self.users = {}
        else:
            # Створюємо директорію якщо не існує
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self.users = {}
    
    def save_data(self):
        """Збереження даних користувачів у файл"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        data = {
            'users': self.users
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register(self, username: str, password: str) -> bool:
        """
        Реєстрація нового користувача
        
        Args:
            username: Ім'я користувача
            password: Пароль
            
        Returns:
            True якщо реєстрація успішна, False якщо користувач вже існує
        """
        if username in self.users:
            return False
        
        self.users[username] = {
            'password_hash': self._hash_password(password),
            'is_admin': False,
            'created_at': str(os.path.getmtime(self.data_file) if os.path.exists(self.data_file) else 0)
        }
        self.save_data()
        return True
    
    def login(self, username: str, password: str) -> bool:
        """
        Авторизація користувача
        
        Args:
            username: Ім'я користувача
            password: Пароль
            
        Returns:
            True якщо авторизація успішна, False інакше
        """
        if username not in self.users:
            return False
        
        password_hash = self._hash_password(password)
        if self.users[username]['password_hash'] == password_hash:
            self.current_user = username
            return True
        return False
    
    def logout(self):
        """Вихід з системи"""
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Перевірка чи користувач авторизований"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[str]:
        """Отримання поточного користувача"""
        return self.current_user
    
    def is_admin(self, username: Optional[str] = None) -> bool:
        """
        Перевірка чи користувач є адміністратором
        
        Args:
            username: Ім'я користувача (якщо None, перевіряється поточний)
        """
        user = username or self.current_user
        if user and user in self.users:
            return self.users[user].get('is_admin', False)
        return False
    
    def set_admin(self, username: str, is_admin: bool = True):
        """
        Встановлення прав адміністратора
        
        Args:
            username: Ім'я користувача
            is_admin: True для надання прав адміністратора
        """
        if username in self.users:
            self.users[username]['is_admin'] = is_admin
            self.save_data()
    
    def list_users(self) -> list:
        """Отримання списку всіх користувачів"""
        return list(self.users.keys())

