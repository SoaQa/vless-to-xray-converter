"""
Модуль утилит

Содержит вспомогательные функции для работы с файлами и другими задачами.
"""

import json
import sys


def save_to_file(data: dict, filename: str):
    """
    Сохраняет данные в файл
    
    Args:
        data: Данные для сохранения
        filename: Имя файла
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Конфигурация сохранена в файл: {filename}")
    except Exception as e:
        print(f"Ошибка сохранения файла: {e}")
        sys.exit(1)


def format_json_output(data: dict) -> str:
    """
    Форматирует данные в JSON строку для вывода
    
    Args:
        data: Данные для форматирования
        
    Returns:
        Отформатированная JSON строка
    """
    return json.dumps(data, indent=4, ensure_ascii=False) 