#!/usr/bin/env python3
"""
Головний файл запуску операційної оболонки Take-Grant
"""

import os
import sys

# Додаємо поточну директорію до шляху
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.auth import AuthenticationModule
from modules.objects import ObjectIdentifier
from modules.access_graph import AccessGraph
from modules.security_kernel import SecurityKernel
from modules.operations import OperationsModule
from modules.admin import AdminModule
from modules.audit import AuditModule
from modules.cli import CLI


def main():
    """Головна функція"""
    # Ініціалізація всіх модулів
    print("Ініціалізація системи...")
    
    # Визначаємо шляхи до файлів даних
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    logs_dir = os.path.join(base_dir, "logs")
    
    # Створюємо директорії якщо не існують
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    
    data_file = os.path.join(data_dir, "system.json")
    audit_log = os.path.join(logs_dir, "audit.log")
    audit_json = os.path.join(data_dir, "audit.json")
    
    # Ініціалізація модулів
    auth_module = AuthenticationModule(data_file)
    object_identifier = ObjectIdentifier()
    access_graph = AccessGraph()
    security_kernel = SecurityKernel(access_graph)
    operations_module = OperationsModule(
        object_identifier, access_graph, security_kernel
    )
    admin_module = AdminModule(
        auth_module, object_identifier, access_graph, security_kernel
    )
    audit_module = AuditModule(audit_log, audit_json)
    
    # Завантаження даних (якщо потрібно)
    # TODO: Додати завантаження графа доступу та об'єктів з файлу
    
    # Створення та запуск CLI
    cli = CLI(
        auth_module,
        object_identifier,
        access_graph,
        security_kernel,
        operations_module,
        admin_module,
        audit_module
    )
    
    print("Система готова до роботи!\n")
    cli.run()
    
    # Збереження даних перед виходом
    print("\nЗбереження даних...")
    auth_module.save_data()
    audit_module.save_events()
    # TODO: Додати збереження графа доступу та об'єктів
    print("Дані збережено.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограму перервано користувачем.")
        sys.exit(0)
    except Exception as e:
        print(f"\nКритична помилка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

