"""
Модуль адміністратора для управління системою
"""

from typing import List, Optional
from .auth import AuthenticationModule
from .objects import ObjectIdentifier
from .access_graph import AccessGraph, AccessRight
from .security_kernel import SecurityKernel


class AdminModule:
    """
    Модуль адміністратора для управління суб'єктами, об'єктами та правами доступу
    """
    
    def __init__(self, auth_module: AuthenticationModule,
                 object_identifier: ObjectIdentifier,
                 access_graph: AccessGraph,
                 security_kernel: SecurityKernel):
        """
        Ініціалізація модуля адміністратора
        
        Args:
            auth_module: Модуль автентифікації
            object_identifier: Модуль ідентифікації об'єктів
            access_graph: Граф доступу
            security_kernel: Ядро безпеки
        """
        self.auth_module = auth_module
        self.object_identifier = object_identifier
        self.access_graph = access_graph
        self.security_kernel = security_kernel
    
    def is_admin(self, username: str) -> bool:
        """Перевірка чи користувач є адміністратором"""
        return self.auth_module.is_admin(username)
    
    def set_user_admin(self, admin_username: str, target_username: str, 
                      is_admin: bool = True) -> bool:
        """
        Встановлення прав адміністратора для користувача
        
        Args:
            admin_username: Ім'я адміністратора
            target_username: Ім'я користувача
            is_admin: True для надання прав адміністратора
            
        Returns:
            True якщо операція успішна
        """
        if not self.is_admin(admin_username):
            return False
        
        self.auth_module.set_admin(target_username, is_admin)
        return True
    
    def list_all_users(self, admin_username: str) -> List[str]:
        """
        Отримання списку всіх користувачів
        
        Args:
            admin_username: Ім'я адміністратора
            
        Returns:
            Список імен користувачів
        """
        if not self.is_admin(admin_username):
            return []
        
        return self.auth_module.list_users()
    
    def list_all_objects(self, admin_username: str) -> List[dict]:
        """
        Отримання списку всіх об'єктів
        
        Args:
            admin_username: Ім'я адміністратора
            
        Returns:
            Список об'єктів
        """
        if not self.is_admin(admin_username):
            return []
        
        return self.object_identifier.list_objects()
    
    def grant_rights(self, admin_username: str, subject_id: str, 
                    object_id: str, rights: set) -> bool:
        """
        Надання прав доступу (адміністративна операція)
        
        Args:
            admin_username: Ім'я адміністратора
            subject_id: ID суб'єкта
            object_id: ID об'єкта
            rights: Множина прав доступу
            
        Returns:
            True якщо операція успішна
        """
        if not self.is_admin(admin_username):
            return False
        
        for right in rights:
            self.access_graph.add_right(subject_id, object_id, right)
        
        return True
    
    def revoke_rights(self, admin_username: str, subject_id: str,
                     object_id: str, rights: set) -> bool:
        """
        Відкликання прав доступу (адміністративна операція)
        
        Args:
            admin_username: Ім'я адміністратора
            subject_id: ID суб'єкта
            object_id: ID об'єкта
            rights: Множина прав для відкликання
            
        Returns:
            True якщо операція успішна
        """
        if not self.is_admin(admin_username):
            return False
        
        for right in rights:
            self.access_graph.remove_right(subject_id, object_id, right)
        
        return True
    
    def get_access_matrix(self, admin_username: str) -> List[dict]:
        """
        Отримання матриці доступу
        
        Args:
            admin_username: Ім'я адміністратора
            
        Returns:
            Список записів матриці доступу
        """
        if not self.is_admin(admin_username):
            return []
        
        matrix = []
        for (subject_id, object_id), rights in self.access_graph.graph.items():
            matrix.append({
                'subject': subject_id,
                'object': object_id,
                'rights': [r.value for r in rights]
            })
        
        return matrix
    
    def delete_user(self, admin_username: str, target_username: str) -> bool:
        """
        Видалення користувача (тільки якщо він не має об'єктів)
        
        Args:
            admin_username: Ім'я адміністратора
            target_username: Ім'я користувача для видалення
            
        Returns:
            True якщо видалення успішне
        """
        if not self.is_admin(admin_username):
            return False
        
        if target_username == admin_username:
            return False  # Не можна видалити себе
        
        # Перевірка чи користувач має об'єкти
        user_objects = self.object_identifier.get_objects_by_owner(target_username)
        if user_objects:
            return False  # Не можна видалити користувача з об'єктами
        
        # Видалення користувача (в реальній системі тут була б логіка видалення)
        # Для спрощення просто повертаємо True
        return True

