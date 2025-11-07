"""
Модуль однозначної ідентифікації об'єктів
"""

import uuid
from typing import Dict, Set, Optional
from enum import Enum


class ObjectType(Enum):
    """Типи об'єктів у системі"""
    FILE = "file"
    DIRECTORY = "directory"
    SUBJECT = "subject"  # Суб'єкт також є об'єктом


class ObjectIdentifier:
    """Модуль для ідентифікації об'єктів"""
    
    def __init__(self):
        """Ініціалізація модуля ідентифікації"""
        self.objects: Dict[str, Dict] = {}  # object_id -> {type, name, owner, ...}
        self.name_to_id: Dict[str, str] = {}  # name -> object_id (для швидкого пошуку)
    
    def generate_id(self) -> str:
        """Генерація унікального ідентифікатора об'єкта"""
        return str(uuid.uuid4())
    
    def create_object(self, name: str, obj_type: ObjectType, owner: str, 
                     parent_id: Optional[str] = None) -> str:
        """
        Створення нового об'єкта
        
        Args:
            name: Ім'я об'єкта
            obj_type: Тип об'єкта
            owner: Власник об'єкта
            parent_id: ID батьківського об'єкта (для файлів/каталогів)
            
        Returns:
            ID створеного об'єкта
        """
        # Перевірка на унікальність імені
        if name in self.name_to_id:
            raise ValueError(f"Об'єкт з ім'ям '{name}' вже існує")
        
        object_id = self.generate_id()
        self.objects[object_id] = {
            'id': object_id,
            'name': name,
            'type': obj_type.value,
            'owner': owner,
            'parent_id': parent_id,
            'created_at': str(uuid.uuid1().time)
        }
        self.name_to_id[name] = object_id
        return object_id
    
    def get_object(self, identifier: str) -> Optional[Dict]:
        """
        Отримання об'єкта за ID або ім'ям
        
        Args:
            identifier: ID або ім'я об'єкта
            
        Returns:
            Словник з даними об'єкта або None
        """
        # Спочатку перевіряємо чи це ID
        if identifier in self.objects:
            return self.objects[identifier]
        
        # Якщо ні, шукаємо за ім'ям
        if identifier in self.name_to_id:
            object_id = self.name_to_id[identifier]
            return self.objects[object_id]
        
        return None
    
    def get_object_id(self, identifier: str) -> Optional[str]:
        """
        Отримання ID об'єкта за ім'ям або ID
        
        Args:
            identifier: Ім'я або ID об'єкта
            
        Returns:
            ID об'єкта або None
        """
        if identifier in self.objects:
            return identifier
        
        if identifier in self.name_to_id:
            return self.name_to_id[identifier]
        
        return None
    
    def delete_object(self, identifier: str) -> bool:
        """
        Видалення об'єкта
        
        Args:
            identifier: ID або ім'я об'єкта
            
        Returns:
            True якщо видалення успішне
        """
        object_id = self.get_object_id(identifier)
        if not object_id:
            return False
        
        obj = self.objects[object_id]
        name = obj['name']
        
        # Видаляємо з обох словників
        del self.objects[object_id]
        if name in self.name_to_id:
            del self.name_to_id[name]
        
        return True
    
    def list_objects(self, obj_type: Optional[ObjectType] = None, 
                    owner: Optional[str] = None) -> list:
        """
        Отримання списку об'єктів з фільтрацією
        
        Args:
            obj_type: Фільтр за типом (None - всі типи)
            owner: Фільтр за власником (None - всі власники)
            
        Returns:
            Список об'єктів
        """
        result = []
        for obj in self.objects.values():
            if obj_type and obj['type'] != obj_type.value:
                continue
            if owner and obj['owner'] != owner:
                continue
            result.append(obj)
        return result
    
    def get_objects_by_owner(self, owner: str) -> list:
        """Отримання всіх об'єктів власника"""
        return self.list_objects(owner=owner)
    
    def object_exists(self, identifier: str) -> bool:
        """Перевірка існування об'єкта"""
        return self.get_object(identifier) is not None

