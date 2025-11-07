#!/usr/bin/env python3
"""
Скрипт для генерації лістингу програмного продукту
"""

import os
from pathlib import Path


def generate_listing(output_file="ЛІСТИНГ_ПРОГРАМИ.txt"):
    """Генерація лістингу всіх файлів проекту"""
    
    base_dir = Path(__file__).parent
    output_path = base_dir.parent / output_file
    
    # Файли для включення (тільки .py файли)
    files_to_include = [
        "main.py",
        "modules/auth.py",
        "modules/objects.py",
        "modules/access_graph.py",
        "modules/security_kernel.py",
        "modules/operations.py",
        "modules/admin.py",
        "modules/audit.py",
        "modules/cli.py",
    ]
    
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("=" * 80 + "\n")
        out.write("ЛІСТИНГ ПРОГРАМНОГО ПРОДУКТУ\n")
        out.write("Операційна оболонка з моделлю Take-Grant\n")
        out.write("=" * 80 + "\n\n")
        
        for file_path in files_to_include:
            full_path = base_dir / file_path
            
            if not full_path.exists():
                continue
            
            out.write("\n" + "=" * 80 + "\n")
            out.write(f"Файл: {file_path}\n")
            out.write("=" * 80 + "\n\n")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # Формат: номер рядка | вміст
                    out.write(f"{i:4d} | {line}")
            
            out.write("\n")
    
    print(f"Лістинг згенеровано: {output_path}")
    print(f"Загальна кількість файлів: {len(files_to_include)}")


if __name__ == "__main__":
    generate_listing()

