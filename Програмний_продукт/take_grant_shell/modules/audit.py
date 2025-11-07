"""
Модуль аудиту подій - журнал подій системи
"""

import os
import json
from datetime import datetime
from typing import List, Optional
from enum import Enum


class EventType(Enum):
    """Типи подій для аудиту"""
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    CREATE_OBJECT = "create_object"
    DELETE_OBJECT = "delete_object"
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    EXECUTE_FILE = "execute_file"
    TAKE_OPERATION = "take"
    GRANT_OPERATION = "grant"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    ADMIN_ACTION = "admin_action"


class AuditModule:
    """
    Модуль аудиту для протоколювання подій системи
    """
    
    def __init__(self, log_file: str = "logs/audit.log",
                 json_file: str = "data/audit.json"):
        """
        Ініціалізація модуля аудиту
        
        Args:
            log_file: Шлях до текстового лог-файлу
            json_file: Шлях до JSON файлу з подіями
        """
        self.log_file = log_file
        self.json_file = json_file
        self.events: List[dict] = []
        self.load_events()
    
    def load_events(self):
        """Завантаження подій з JSON файлу"""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.events = data.get('events', [])
            except (json.JSONDecodeError, IOError):
                self.events = []
        else:
            os.makedirs(os.path.dirname(self.json_file), exist_ok=True)
            self.events = []
    
    def save_events(self):
        """Збереження подій у JSON файл"""
        os.makedirs(os.path.dirname(self.json_file), exist_ok=True)
        data = {'events': self.events}
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def log_event(self, event_type: EventType, subject: str, 
                  details: dict = None, success: bool = True):
        """
        Протоколювання події
        
        Args:
            event_type: Тип події
            subject: Суб'єкт, який виконав дію
            details: Додаткові деталі події
            success: Чи була операція успішною
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type.value,
            'subject': subject,
            'success': success,
            'details': details or {}
        }
        
        self.events.append(event)
        
        # Зберігаємо у JSON
        self.save_events()
        
        # Записуємо у текстовий лог
        self._write_log(event)
    
    def _write_log(self, event: dict):
        """Запис події у текстовий лог-файл"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        status = "SUCCESS" if event['success'] else "FAILED"
        details_str = ""
        if event['details']:
            details_str = " | " + ", ".join([f"{k}={v}" for k, v in event['details'].items()])
        
        log_line = f"[{event['timestamp']}] {status} | {event['type']} | " \
                  f"subject={event['subject']}{details_str}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
    
    def get_events(self, event_type: Optional[EventType] = None,
                   subject: Optional[str] = None,
                   success_only: bool = False,
                   failed_only: bool = False) -> List[dict]:
        """
        Отримання подій з фільтрацією
        
        Args:
            event_type: Фільтр за типом події
            subject: Фільтр за суб'єктом
            success_only: Тільки успішні події
            failed_only: Тільки неуспішні події
            
        Returns:
            Список подій
        """
        result = self.events.copy()
        
        if event_type:
            result = [e for e in result if e['type'] == event_type.value]
        
        if subject:
            result = [e for e in result if e['subject'] == subject]
        
        if success_only:
            result = [e for e in result if e['success']]
        
        if failed_only:
            result = [e for e in result if not e['success']]
        
        return result
    
    def get_failed_accesses(self) -> List[dict]:
        """Отримання всіх неуспішних спроб доступу"""
        return self.get_events(event_type=EventType.ACCESS_DENIED)
    
    def get_successful_operations(self) -> List[dict]:
        """Отримання всіх успішних операцій"""
        return [e for e in self.events if e['success']]
    
    def get_all_events(self) -> List[dict]:
        """Отримання всіх подій"""
        return self.events.copy()
    
    def clear_events(self):
        """Очищення журналу подій"""
        self.events = []
        self.save_events()
        
        # Очищаємо текстовий лог
        if os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")

