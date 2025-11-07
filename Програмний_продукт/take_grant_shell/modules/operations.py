"""
Модуль операцій над об'єктами (симуляція файлової системи)
"""

from typing import Dict, Optional
from .objects import ObjectIdentifier, ObjectType
from .access_graph import AccessGraph, AccessRight
from .security_kernel import SecurityKernel


class OperationsModule:
    """
    Модуль для виконання операцій над об'єктами
    Симулює файлову систему з контролем доступу
    """
    
    def __init__(self, object_identifier: ObjectIdentifier,
                 access_graph: AccessGraph,
                 security_kernel: SecurityKernel):
        """
        Ініціалізація модуля операцій
        
        Args:
            object_identifier: Модуль ідентифікації об'єктів
            access_graph: Граф доступу
            security_kernel: Ядро безпеки
        """
        self.object_identifier = object_identifier
        self.access_graph = access_graph
        self.security_kernel = security_kernel
        # Симуляція вмісту файлів: object_id -> content
        self.file_contents: Dict[str, str] = {}
    
    def read_file(self, subject_id: str, object_id: str) -> Optional[str]:
        """
        Читання файлу
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта (файлу)
            
        Returns:
            Вміст файлу або None якщо доступ заборонено
        """
        # Перевірка доступу
        if not self.security_kernel.can_access(subject_id, object_id, 
                                               AccessRight.READ):
            return None
        
        obj = self.object_identifier.get_object(object_id)
        if not obj or obj['type'] != ObjectType.FILE.value:
            return None
        
        return self.file_contents.get(object_id, "")
    
    def write_file(self, subject_id: str, object_id: str, content: str) -> bool:
        """
        Запис у файл
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта (файлу)
            content: Вміст для запису
            
        Returns:
            True якщо запис успішний
        """
        # Перевірка доступу
        if not self.security_kernel.can_access(subject_id, object_id,
                                              AccessRight.WRITE):
            return False
        
        obj = self.object_identifier.get_object(object_id)
        if not obj or obj['type'] != ObjectType.FILE.value:
            return False
        
        self.file_contents[object_id] = content
        return True
    
    def execute_file(self, subject_id: str, object_id: str) -> bool:
        """
        Виконання файлу
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта (файлу)
            
        Returns:
            True якщо виконання дозволено
        """
        # Перевірка доступу
        if not self.security_kernel.can_access(subject_id, object_id,
                                              AccessRight.EXECUTE):
            return False
        
        obj = self.object_identifier.get_object(object_id)
        if not obj or obj['type'] != ObjectType.FILE.value:
            return False
        
        # Симуляція виконання (в реальній системі тут була б виконана програма)
        return True
    
    def create_file(self, subject_id: str, name: str, 
                   parent_id: Optional[str] = None) -> Optional[str]:
        """
        Створення файлу
        
        Args:
            subject_id: ID суб'єкта
            name: Ім'я файлу
            parent_id: ID батьківського каталогу
            
        Returns:
            ID створеного файлу або None
        """
        try:
            object_id = self.object_identifier.create_object(
                name, ObjectType.FILE, subject_id, parent_id
            )
            
            # При створенні власник отримує всі права
            self.access_graph.create(subject_id, object_id)
            
            # Ініціалізуємо порожній вміст
            self.file_contents[object_id] = ""
            
            return object_id
        except ValueError:
            return None
    
    def create_directory(self, subject_id: str, name: str,
                        parent_id: Optional[str] = None) -> Optional[str]:
        """
        Створення каталогу
        
        Args:
            subject_id: ID суб'єкта
            name: Ім'я каталогу
            parent_id: ID батьківського каталогу
            
        Returns:
            ID створеного каталогу або None
        """
        try:
            object_id = self.object_identifier.create_object(
                name, ObjectType.DIRECTORY, subject_id, parent_id
            )
            
            # При створенні власник отримує всі права
            self.access_graph.create(subject_id, object_id)
            
            return object_id
        except ValueError:
            return None
    
    def delete_object(self, subject_id: str, object_id: str) -> bool:
        """
        Видалення об'єкта
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта
            
        Returns:
            True якщо видалення успішне
        """
        obj = self.object_identifier.get_object(object_id)
        if not obj:
            return False
        
        # Перевірка: тільки власник може видалити об'єкт
        if obj['owner'] != subject_id:
            # Або перевіряємо чи має право OWN
            if not self.security_kernel.can_access(subject_id, object_id,
                                                  AccessRight.OWN):
                return False
        
        # Видаляємо з файлової системи
        if object_id in self.file_contents:
            del self.file_contents[object_id]
        
        # Видаляємо всі права доступу до цього об'єкта
        edges_to_remove = []
        for (s, o), rights in self.access_graph.graph.items():
            if o == object_id:
                edges_to_remove.append((s, o))
        
        for s, o in edges_to_remove:
            del self.access_graph.graph[(s, o)]
        
        # Видаляємо з ідентифікатора
        return self.object_identifier.delete_object(object_id)
    
    def list_directory(self, subject_id: str, directory_id: str) -> list:
        """
        Отримання списку об'єктів у каталозі
        
        Args:
            subject_id: ID суб'єкта
            directory_id: ID каталогу
            
        Returns:
            Список об'єктів у каталозі
        """
        # Перевірка доступу до каталогу
        if not self.security_kernel.can_access(subject_id, directory_id,
                                              AccessRight.READ):
            return []
        
        obj = self.object_identifier.get_object(directory_id)
        if not obj or obj['type'] != ObjectType.DIRECTORY.value:
            return []
        
        # Знаходимо всі об'єкти з цим батьківським каталогом
        all_objects = self.object_identifier.list_objects()
        result = []
        for obj in all_objects:
            if obj.get('parent_id') == directory_id:
                result.append(obj)
        
        return result
    
    def get_file_content(self, object_id: str) -> str:
        """Отримання вмісту файлу (без перевірки доступу)"""
        return self.file_contents.get(object_id, "")

