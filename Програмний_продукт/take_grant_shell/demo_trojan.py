#!/usr/bin/env python3
"""
Демонстрація вразливості моделі Take-Grant до троянів

Цей скрипт імітує поведінку трояна, який використовує права користувача
для надання доступу зловмиснику.
"""

import sys
import os

# Додаємо шлях до модулів
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.auth import AuthenticationModule
from modules.objects import ObjectIdentifier
from modules.access_graph import AccessGraph, AccessRight
from modules.security_kernel import SecurityKernel
from modules.operations import OperationsModule
from modules.audit import AuditModule


def demonstrate_trojan_vulnerability():
    """
    Демонстрація як троян може використати права користувача
    для надання доступу зловмиснику
    """
    
    print("=" * 80)
    print("ДЕМОНСТРАЦІЯ ВРАЗЛИВОСТІ ДО ТРОЯНІВ")
    print("=" * 80)
    print()
    
    # Ініціалізація системи
    auth = AuthenticationModule("data/demo_system.json")
    objects = ObjectIdentifier()
    graph = AccessGraph()
    security = SecurityKernel(graph)
    ops = OperationsModule(objects, graph, security)
    audit = AuditModule("logs/demo_audit.log", "data/demo_audit.json")
    
    # Крок 1: Реєстрація законного користувача
    print("Крок 1: Реєстрація законного користувача 'alice'")
    auth.register("alice", "password123")
    auth.login("alice", "password123")
    print("✅ Користувач 'alice' зареєстровано та авторизовано\n")
    
    # Крок 2: Alice створює конфіденційний файл
    print("Крок 2: Alice створює конфіденційний файл 'secret.txt'")
    file_id = ops.create_file("alice", "secret.txt")
    ops.write_file("alice", file_id, "CONFIDENTIAL DATA: Credit card numbers, passwords, etc.")
    print(f"✅ Файл створено (ID: {file_id})")
    print(f"   Вміст: {ops.read_file('alice', file_id)}\n")
    
    # Крок 3: Alice має повні права до файлу
    print("Крок 3: Перевірка прав Alice до файлу")
    rights = graph.get_rights("alice", file_id)
    print(f"   Права Alice: {[r.value for r in rights]}")
    print("   ✅ Alice має права r,w,x,t,g,o (всі права)\n")
    
    # Крок 4: Реєстрація зловмисника
    print("Крок 4: Реєстрація зловмисника 'attacker'")
    auth.register("attacker", "evil123")
    print("   ⚠️  Зловмисник 'attacker' зареєстровано\n")
    
    # Крок 5: Alice запускає "троян" (імітація)
    print("Крок 5: Alice запускає програму (яка виявляється трояном)")
    print("   ⚠️  Троян отримує права користувача 'alice'\n")
    
    # Крок 6: Троян використовує права Alice для grant доступу
    print("Крок 6: Троян використовує права Alice для надання доступу зловмиснику")
    print("   Виконується: grant(secret.txt, attacker, r,w)")
    
    # Троян використовує права alice
    success = graph.grant("alice", file_id, "attacker", 
                         {AccessRight.READ, AccessRight.WRITE})
    
    if success:
        print("   ✅ Троян успішно надав доступ зловмиснику!")
        print("   ⚠️  Alice НЕ ЗНАЄ про це!\n")
    else:
        print("   ❌ Операція не вдалася\n")
    
    # Крок 7: Зловмисник отримує доступ
    print("Крок 7: Зловмисник отримує доступ до конфіденційних даних")
    auth.logout()
    auth.login("attacker", "evil123")
    
    can_read = security.can_access("attacker", file_id, AccessRight.READ)
    if can_read:
        print("   ✅ Зловмисник має доступ!")
        content = ops.read_file("attacker", file_id)
        print(f"   📄 Вміст файлу: {content}")
        print("   ⚠️  КОНФІДЕНЦІЙНІ ДАНІ СКОМПРОМЕТОВАНО!\n")
    else:
        print("   ❌ Доступ заборонено\n")
    
    # Крок 8: Перевірка матриці доступу
    print("Крок 8: Матриця доступу після атаки")
    print("   Права до secret.txt:")
    for (subject, obj), rights in graph.graph.items():
        if obj == file_id:
            print(f"      {subject}: {[r.value for r in rights]}")
    
    print()
    print("=" * 80)
    print("ВИСНОВОК:")
    print("=" * 80)
    print("Дискреційна модель Take-Grant НЕ ЗАХИЩАЄ від програм,")
    print("які виконуються від імені авторизованого користувача.")
    print("Троян може використати права користувача для надання")
    print("доступу зловмиснику без відома користувача.")
    print("=" * 80)


if __name__ == "__main__":
    try:
        demonstrate_trojan_vulnerability()
    except Exception as e:
        print(f"Помилка: {e}")
        import traceback
        traceback.print_exc()

