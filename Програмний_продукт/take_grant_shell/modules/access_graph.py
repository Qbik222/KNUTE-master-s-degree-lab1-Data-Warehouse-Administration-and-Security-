"""
Модуль графа доступу для моделі Take-Grant
"""

from typing import Dict, Set, Optional, List, Tuple
from enum import Enum


class AccessRight(Enum):
    """Права доступу в моделі Take-Grant"""
    READ = "r"      # Читання
    WRITE = "w"     # Запис
    EXECUTE = "x"   # Виконання
    TAKE = "t"      # Право брати права
    GRANT = "g"     # Право надавати права
    OWN = "o"       # Право власності


class AccessGraph:
    """
    Граф доступу для моделі Take-Grant
    
    Граф представлений як словник, де ключ - це пара (subject_id, object_id),
    а значення - множина прав доступу.
    """
    
    def __init__(self):
        """Ініціалізація графа доступу"""
        # Граф: (subject_id, object_id) -> Set[AccessRight]
        self.graph: Dict[Tuple[str, str], Set[AccessRight]] = {}
        # Для швидкого пошуку: subject_id -> Set[object_id]
        self.subject_edges: Dict[str, Set[str]] = {}
        # Для швидкого пошуку: object_id -> Set[subject_id]
        self.object_edges: Dict[str, Set[str]] = {}
    
    def _normalize_edge(self, subject_id: str, object_id: str) -> Tuple[str, str]:
        """Нормалізація ребра графа"""
        return (subject_id, object_id)
    
    def add_right(self, subject_id: str, object_id: str, right: AccessRight):
        """
        Додавання права доступу
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта
            right: Право доступу
        """
        edge = self._normalize_edge(subject_id, object_id)
        
        if edge not in self.graph:
            self.graph[edge] = set()
        
        self.graph[edge].add(right)
        
        # Оновлюємо індекси для швидкого пошуку
        if subject_id not in self.subject_edges:
            self.subject_edges[subject_id] = set()
        self.subject_edges[subject_id].add(object_id)
        
        if object_id not in self.object_edges:
            self.object_edges[object_id] = set()
        self.object_edges[object_id].add(subject_id)
    
    def remove_right(self, subject_id: str, object_id: str, right: AccessRight):
        """
        Видалення права доступу
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта
            right: Право доступу
        """
        edge = self._normalize_edge(subject_id, object_id)
        
        if edge in self.graph:
            self.graph[edge].discard(right)
            
            # Якщо множина прав порожня, видаляємо ребро
            if not self.graph[edge]:
                del self.graph[edge]
                self.subject_edges[subject_id].discard(object_id)
                self.object_edges[object_id].discard(subject_id)
    
    def has_right(self, subject_id: str, object_id: str, right: AccessRight) -> bool:
        """
        Перевірка наявності права доступу
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта
            right: Право доступу
            
        Returns:
            True якщо право існує
        """
        edge = self._normalize_edge(subject_id, object_id)
        return edge in self.graph and right in self.graph[edge]
    
    def get_rights(self, subject_id: str, object_id: str) -> Set[AccessRight]:
        """
        Отримання всіх прав суб'єкта до об'єкта
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта
            
        Returns:
            Множина прав доступу
        """
        edge = self._normalize_edge(subject_id, object_id)
        return self.graph.get(edge, set())
    
    def take(self, subject_id: str, source_object_id: str, target_object_id: str, 
             rights: Set[AccessRight]) -> bool:
        """
        Операція Take: суб'єкт бере права від source_object до target_object
        
        Правило: Якщо subject має право 't' до source_object, і source_object
        має права до target_object, то subject може отримати ці права.
        
        Args:
            subject_id: ID суб'єкта, який виконує операцію
            source_object_id: ID об'єкта, від якого беруться права
            target_object_id: ID об'єкта, до якого беруться права
            rights: Множина прав, які потрібно взяти
            
        Returns:
            True якщо операція успішна
        """
        # Перевірка: чи має subject право 't' до source_object
        if not self.has_right(subject_id, source_object_id, AccessRight.TAKE):
            return False
        
        # Перевірка: чи має source_object права до target_object
        source_rights = self.get_rights(source_object_id, target_object_id)
        if not source_rights:
            return False
        
        # Беремо тільки ті права, які є у source_object
        available_rights = rights.intersection(source_rights)
        
        # Додаємо права subject до target_object
        for right in available_rights:
            self.add_right(subject_id, target_object_id, right)
        
        return len(available_rights) > 0
    
    def grant(self, subject_id: str, source_object_id: str, target_subject_id: str,
              rights: Set[AccessRight]) -> bool:
        """
        Операція Grant: суб'єкт надає права від source_object іншому суб'єкту
        
        Правило: Якщо subject має право 'g' до source_object, і subject має
        права до source_object, то subject може надати ці права target_subject.
        
        Args:
            subject_id: ID суб'єкта, який виконує операцію
            source_object_id: ID об'єкта, права від якого надаються
            target_subject_id: ID суб'єкта, якому надаються права
            rights: Множина прав, які потрібно надати
            
        Returns:
            True якщо операція успішна
        """
        # Перевірка: чи має subject право 'g' до source_object
        if not self.has_right(subject_id, source_object_id, AccessRight.GRANT):
            return False
        
        # Перевірка: чи має subject права до source_object
        subject_rights = self.get_rights(subject_id, source_object_id)
        if not subject_rights:
            return False
        
        # Надаємо тільки ті права, які є у subject
        available_rights = rights.intersection(subject_rights)
        
        # Додаємо права target_subject до source_object
        for right in available_rights:
            self.add_right(target_subject_id, source_object_id, right)
        
        return len(available_rights) > 0
    
    def create(self, subject_id: str, object_id: str, 
               rights: Set[AccessRight] = None) -> bool:
        """
        Операція Create: суб'єкт створює об'єкт і отримує до нього всі права
        
        Args:
            subject_id: ID суб'єкта, який створює об'єкт
            object_id: ID створюваного об'єкта
            rights: Права доступу (за замовчуванням всі)
            
        Returns:
            True якщо операція успішна
        """
        if rights is None:
            # За замовчуванням надаємо всі права
            rights = {AccessRight.READ, AccessRight.WRITE, AccessRight.EXECUTE,
                     AccessRight.TAKE, AccessRight.GRANT, AccessRight.OWN}
        
        for right in rights:
            self.add_right(subject_id, object_id, right)
        
        return True
    
    def remove(self, subject_id: str, object_id: str, rights: Set[AccessRight]):
        """
        Операція Remove: видалення прав доступу
        
        Args:
            subject_id: ID суб'єкта
            object_id: ID об'єкта
            rights: Множина прав для видалення
        """
        for right in rights:
            self.remove_right(subject_id, object_id, right)
    
    def get_all_edges(self) -> List[Tuple[str, str, Set[AccessRight]]]:
        """
        Отримання всіх ребер графа
        
        Returns:
            Список кортежів (subject_id, object_id, rights)
        """
        result = []
        for (subject_id, object_id), rights in self.graph.items():
            if rights:  # Тільки якщо є права
                result.append((subject_id, object_id, rights))
        return result
    
    def get_subject_objects(self, subject_id: str) -> Set[str]:
        """Отримання всіх об'єктів, до яких має доступ суб'єкт"""
        return self.subject_edges.get(subject_id, set())
    
    def get_object_subjects(self, object_id: str) -> Set[str]:
        """Отримання всіх суб'єктів, які мають доступ до об'єкта"""
        return self.object_edges.get(object_id, set())

