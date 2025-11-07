"""
Модуль ядра безпеки - перевірка доступу з використанням DFS
"""

from typing import Set, Optional, List
from .access_graph import AccessGraph, AccessRight


class SecurityKernel:
    """
    Ядро безпеки для перевірки можливості отримання доступу
    використовуючи алгоритм DFS для пошуку шляхів у графі Take-Grant
    """
    
    def __init__(self, access_graph: AccessGraph):
        """
        Ініціалізація ядра безпеки
        
        Args:
            access_graph: Граф доступу
        """
        self.access_graph = access_graph
    
    def can_access(self, subject_id: str, object_id: str, 
                  required_right: AccessRight) -> bool:
        """
        Перевірка чи може суб'єкт отримати доступ до об'єкта
        
        Використовує DFS для пошуку можливого шляху отримання прав
        через операції take/grant.
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта
            required_right: Необхідне право доступу
            
        Returns:
            True якщо доступ можливий
        """
        # Спочатку перевіряємо чи є пряме право
        if self.access_graph.has_right(subject_id, object_id, required_right):
            return True
        
        # Якщо немає прямого доступу, шукаємо шлях через take/grant
        return self._find_access_path(subject_id, object_id, required_right)
    
    def _find_access_path(self, subject_id: str, object_id: str,
                          required_right: AccessRight) -> bool:
        """
        Пошук шляху отримання доступу через DFS
        
        Алгоритм:
        1. Шукаємо об'єкти, до яких subject має право 't' (take)
        2. Для кожного такого об'єкта перевіряємо чи він має доступ до target
        3. Якщо так, то subject може отримати доступ через take
        4. Аналогічно для grant - шукаємо суб'єктів, які можуть надати доступ
        """
        visited = set()
        return self._dfs_search(subject_id, object_id, required_right, visited)
    
    def _dfs_search(self, current_subject: str, target_object: str,
                   required_right: AccessRight, visited: Set[str]) -> bool:
        """
        Рекурсивний пошук у глибину (DFS)
        
        Args:
            current_subject: Поточний суб'єкт
            target_object: Цільовий об'єкт
            required_right: Необхідне право
            visited: Множина відвіданих вузлів (для уникнення циклів)
            
        Returns:
            True якщо знайдено шлях
        """
        # Уникаємо циклів
        if current_subject in visited:
            return False
        visited.add(current_subject)
        
        # Перевірка прямого доступу
        if self.access_graph.has_right(current_subject, target_object, required_right):
            return True
        
        # Шукаємо через операцію TAKE
        # Знаходимо об'єкти, до яких current_subject має право 't'
        objects_with_take = self.access_graph.get_subject_objects(current_subject)
        
        for intermediate_object in objects_with_take:
            # Перевіряємо чи має current_subject право 't' до intermediate_object
            if not self.access_graph.has_right(current_subject, intermediate_object, 
                                             AccessRight.TAKE):
                continue
            
            # Перевіряємо чи має intermediate_object доступ до target_object
            if self.access_graph.has_right(intermediate_object, target_object, 
                                         required_right):
                # Знайдено шлях через take!
                return True
            
            # Рекурсивно шукаємо далі через intermediate_object
            # (якщо intermediate_object є суб'єктом)
            if self._dfs_search(intermediate_object, target_object, 
                              required_right, visited.copy()):
                return True
        
        # Шукаємо через операцію GRANT
        # Знаходимо суб'єктів, які мають право 'g' до об'єктів з доступом до target
        all_objects = set()
        for (s, o), rights in self.access_graph.graph.items():
            all_objects.add(o)
        
        for intermediate_object in all_objects:
            # Знаходимо суб'єктів, які мають право 'g' до intermediate_object
            subjects_with_grant = self.access_graph.get_object_subjects(intermediate_object)
            
            for grant_subject in subjects_with_grant:
                if not self.access_graph.has_right(grant_subject, intermediate_object,
                                                 AccessRight.GRANT):
                    continue
                
                # Перевіряємо чи має intermediate_object доступ до target_object
                if self.access_graph.has_right(intermediate_object, target_object,
                                             required_right):
                    # Можливий шлях через grant (якщо grant_subject надасть доступ)
                    # Для спрощення вважаємо що це можливо
                    return True
        
        return False
    
    def get_accessible_objects(self, subject_id: str, 
                               required_right: AccessRight) -> List[str]:
        """
        Отримання списку об'єктів, до яких суб'єкт може отримати доступ
        
        Args:
            subject_id: ID суб'єкта
            required_right: Необхідне право
            
        Returns:
            Список ID об'єктів
        """
        accessible = []
        
        # Отримуємо всі об'єкти з графа
        all_objects = set()
        for (s, o), rights in self.access_graph.graph.items():
            all_objects.add(o)
            all_objects.add(s)  # Суб'єкти теж можуть бути об'єктами
        
        for object_id in all_objects:
            if self.can_access(subject_id, object_id, required_right):
                accessible.append(object_id)
        
        return accessible
    
    def check_right(self, subject_id: str, object_id: str, 
                   right: AccessRight) -> bool:
        """
        Перевірка наявності права (з урахуванням можливості отримання)
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта
            right: Право доступу
            
        Returns:
            True якщо право існує або може бути отримане
        """
        return self.can_access(subject_id, object_id, right)

