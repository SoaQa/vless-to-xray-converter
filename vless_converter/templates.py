"""
Модуль для работы с шаблонами

Содержит функции для загрузки и применения шаблонов конфигураций.
"""

import os
import json


def get_available_templates() -> dict:
    """
    Возвращает доступные шаблоны конфигураций
    
    Returns:
        Словарь с доступными шаблонами {простое_имя: путь_к_файлу}
    """
    templates = {
        "openwrt-reverse": "templates/openwrt-reverse-proxy.json"
    }
    return templates


def display_templates_with_numbers() -> dict:
    """
    Отображает доступные шаблоны с номерами
    
    Returns:
        Словарь {номер: имя_шаблона}
    """

    templates = get_available_templates()
    numbered_templates = {}
    
    if templates:
        print("Доступные шаблоны:")
        for i, (name, path) in enumerate(templates.items(), 1):
            print(f"  {i}. {name} - {path}")
            numbered_templates[str(i)] = name
        print()
    
    return numbered_templates


def resolve_template_name(input_value: str) -> str:
    """
    Определяет имя шаблона по номеру или имени
    
    Args:
        input_value: Номер или имя шаблона
        
    Returns:
        Имя шаблона
    """
    templates = get_available_templates()
    numbered_templates = {}
    
    # Создаем mapping номер -> имя
    for i, name in enumerate(templates.keys(), 1):
        numbered_templates[str(i)] = name
    
    # Проверяем, является ли input номером
    if input_value.isdigit() and input_value in numbered_templates:
        return numbered_templates[input_value]
    
    # Проверяем, является ли input именем шаблона
    if input_value in templates:
        return input_value
    
    # Если ничего не подошло, выбрасываем ошибку
    available_options = []
    for i, name in enumerate(templates.keys(), 1):
        available_options.append(f"{i} ({name})")
    
    raise ValueError(f"Неверное название или номер шаблона '{input_value}'. Доступные: {', '.join(available_options)}")


def load_template(template_name: str) -> dict:
    """
    Загружает шаблон конфигурации
    
    Args:
        template_name: Имя шаблона
        
    Returns:
        Словарь с шаблоном конфигурации
    """
    templates = get_available_templates()
    
    if template_name not in templates:
        available = ", ".join(templates.keys())
        raise ValueError(f"Неизвестный шаблон '{template_name}'. Доступные: {available}")
    
    template_path = templates[template_name]
    
    if not os.path.exists(template_path):
        raise ValueError(f"Файл шаблона не найден: {template_path}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка в JSON шаблоне {template_path}: {e}")


def apply_template(template: dict, vless_data: dict, custom_tag: str = None) -> dict:
    """
    Применяет данные VLESS к шаблону
    
    Args:
        template: Шаблон конфигурации
        vless_data: Данные VLESS
        custom_tag: Пользовательский тег (опционально)
        
    Returns:
        Заполненный шаблон
    """
    params = vless_data['params']
    
    # Определяем тег: пользовательский, из фрагмента URL, или 'reverse-proxy' по умолчанию
    if custom_tag:
        tag_to_use = custom_tag
    elif vless_data.get('fragment'):
        tag_to_use = vless_data['fragment']
    else:
        tag_to_use = 'reverse-proxy'
    
    # Подготавливаем данные для замены
    replacements = {
        'address': vless_data['server'],
        'port': str(vless_data['port']),
        'id': vless_data['uuid'],
        'tag': tag_to_use
    }
    
    # Добавляем параметры из URL
    if 'pbk' in params:
        replacements['publicKey'] = params['pbk']
    if 'sni' in params:
        replacements['serverName'] = params['sni']
    if 'fp' in params:
        replacements['fingerprint'] = params['fp']
    else:
        replacements['fingerprint'] = 'chrome'
    if 'sid' in params:
        replacements['shortId'] = params['sid']
    if 'spx' in params:
        replacements['spiderX'] = params['spx']
    else:
        replacements['spiderX'] = '/'
    
    # Конвертируем в JSON строку и заменяем плейсхолдеры
    template_str = json.dumps(template, ensure_ascii=False)
    
    for key, value in replacements.items():
        template_str = template_str.replace(f'{{{{{key}}}}}', value)
    
    # Конвертируем port обратно в число
    template_str = template_str.replace(f'"{vless_data["port"]}"', str(vless_data['port']))
    
    return json.loads(template_str) 