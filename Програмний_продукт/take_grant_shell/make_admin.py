#!/usr/bin/env python3
"""
Скрипт для надання прав адміністратора користувачу
"""

import json
import sys
import os

def make_admin(username: str):
    """Надання прав адміністратора користувачу"""
    
    # Шлях до файлу
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, "data", "system.json")
    
    # Перевірка існування файлу
    if not os.path.exists(data_file):
        print(f"Помилка: файл {data_file} не знайдено")
        return False
    
    # Завантаження даних
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Помилка: не вдалося прочитати {data_file}")
        return False
    
    # Перевірка існування користувача
    if 'users' not in data or username not in data['users']:
        print(f"Помилка: користувач '{username}' не існує")
        print(f"Доступні користувачі: {list(data.get('users', {}).keys())}")
        return False
    
    # Надання прав адміністратора
    data['users'][username]['is_admin'] = True
    
    # Збереження
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Користувач '{username}' тепер адміністратор!")
        return True
    except IOError:
        print(f"Помилка: не вдалося записати {data_file}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Введіть ім'я користувача: ").strip()
    
    if not username:
        print("Помилка: ім'я користувача не може бути порожнім")
        sys.exit(1)
    
    if make_admin(username):
        sys.exit(0)
    else:
        sys.exit(1)

