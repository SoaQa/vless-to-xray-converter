#!/usr/bin/env python3
"""
Скрипт для конвертации VLESS конфигурации в формат Xray
Использование: python vless_to_xray.py "vless://..."
"""

import sys
import json
import urllib.parse
import argparse
import os
from urllib.parse import urlparse, parse_qs


def parse_vless_url(vless_url: str) -> dict:
    """
    Парсит VLESS URL и извлекает все параметры
    
    Args:
        vless_url: Строка VLESS конфигурации
        
    Returns:
        Словарь с параметрами конфигурации
    """
    try:
        # Убираем префикс vless:// если есть
        if vless_url.startswith('vless://'):
            vless_url = vless_url[8:]
        
        # Разделяем на части: uuid@server:port?params#fragment
        if '#' in vless_url:
            main_part, fragment = vless_url.split('#', 1)
            fragment = urllib.parse.unquote(fragment)
        else:
            main_part = vless_url
            fragment = None
        
        # Разделяем на uuid@server:port и параметры
        if '?' in main_part:
            connection_part, query_string = main_part.split('?', 1)
        else:
            connection_part = main_part
            query_string = ''
        
        # Извлекаем uuid, server и port
        if '@' in connection_part:
            uuid, server_part = connection_part.split('@', 1)
        else:
            raise ValueError("Неверный формат VLESS URL: отсутствует @")
        
        # Извлекаем server и port
        if ':' in server_part:
            server, port_str = server_part.split(':', 1)
            try:
                port = int(port_str)
            except ValueError:
                raise ValueError(f"Неверный порт: {port_str}")
        else:
            server = server_part
            port = 443  # Порт по умолчанию
        
        # Парсим query параметры
        params = parse_qs(query_string)
        
        # Преобразуем списки в одиночные значения где это уместно
        parsed_params = {}
        for key, value_list in params.items():
            if len(value_list) == 1:
                parsed_params[key] = value_list[0]
            else:
                parsed_params[key] = value_list
        
        return {
            'uuid': uuid,
            'server': server,
            'port': port,
            'params': parsed_params,
            'fragment': fragment
        }
        
    except Exception as e:
        raise ValueError(f"Ошибка парсинга VLESS URL: {e}")


def create_xray_config(vless_data: dict, tag: str = None) -> dict:
    """
    Создает конфигурацию Xray на основе данных VLESS
    
    Args:
        vless_data: Словарь с данными VLESS
        tag: Тег для конфигурации (опционально)
        
    Returns:
        Словарь конфигурации Xray
    """
    params = vless_data['params']
    
    # Определяем тег: переданный параметр, fragment из URL, или 'proxy' по умолчанию
    if tag:
        config_tag = tag
    elif vless_data.get('fragment'):
        config_tag = vless_data['fragment']
    else:
        config_tag = 'proxy'
    
    # Базовая конфигурация в формате Xray-core
    config = {
        "protocol": "vless",
        "settings": {
            "vnext": [
                {
                    "address": vless_data['server'],
                    "port": vless_data['port'],
                    "users": [
                        {
                            "id": vless_data['uuid'],
                            "encryption": "none"
                        }
                    ]
                }
            ]
        },
        "streamSettings": {
            "network": "tcp",
            "security": "none"
        },
        "tag": config_tag
    }
    
    # Добавляем flow если указан
    if 'flow' in params:
        config['settings']['vnext'][0]['users'][0]['flow'] = params['flow']
    
    # Настраиваем тип соединения
    if 'type' in params:
        config['streamSettings']['network'] = params['type']
    
    # Настраиваем TLS
    if params.get('security') == 'tls':
        config['streamSettings']['security'] = 'tls'
        config['streamSettings']['tlsSettings'] = {
            "allowInsecure": False,
            "serverName": params.get('sni', vless_data['server'])
        }
        
        # Добавляем ALPN
        if 'alpn' in params:
            alpn_values = params['alpn'].split(',')
            config['streamSettings']['tlsSettings']['alpn'] = [value.strip() for value in alpn_values]
        
        # Настраиваем fingerprint
        if 'fp' in params:
            config['streamSettings']['tlsSettings']['fingerprint'] = params['fp']
    
    # Настраиваем REALITY
    elif params.get('security') == 'reality':
        config['streamSettings']['security'] = 'reality'
        config['streamSettings']['realitySettings'] = {}
        
        # Обязательные параметры для Reality
        if 'pbk' in params:
            config['streamSettings']['realitySettings']['publicKey'] = params['pbk']
        
        if 'sni' in params:
            config['streamSettings']['realitySettings']['serverName'] = params['sni']
        
        if 'fp' in params:
            config['streamSettings']['realitySettings']['fingerprint'] = params['fp']
        else:
            config['streamSettings']['realitySettings']['fingerprint'] = 'chrome'
        
        if 'sid' in params:
            config['streamSettings']['realitySettings']['shortId'] = params['sid']
        
        if 'spx' in params:
            config['streamSettings']['realitySettings']['spiderX'] = params['spx']
        else:
            config['streamSettings']['realitySettings']['spiderX'] = '/'
    
    # Настраиваем WebSocket
    if params.get('type') == 'ws':
        config['streamSettings']['wsSettings'] = {
            "path": params.get('path', '/'),
            "headers": {}
        }
        
        if 'host' in params:
            config['streamSettings']['wsSettings']['headers']['Host'] = params['host']
    
    # Настраиваем TCP
    elif params.get('type') == 'tcp':
        if 'headerType' in params:
            config['streamSettings']['tcpSettings'] = {
                "header": {
                    "type": params['headerType']
                }
            }
            
            if params['headerType'] == 'http':
                config['streamSettings']['tcpSettings']['header']['request'] = {
                    "version": "1.1",
                    "method": "GET",
                    "path": [params.get('path', '/')],
                    "headers": {}
                }
                
                if 'host' in params:
                    config['streamSettings']['tcpSettings']['header']['request']['headers']['Host'] = [params['host']]
    
    # Настраиваем gRPC
    elif params.get('type') == 'grpc':
        config['streamSettings']['grpcSettings'] = {
            "serviceName": params.get('serviceName', params.get('path', '')),
            "multiMode": params.get('mode', 'gun') == 'multi'
        }
    
    return config


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


def apply_template(template: dict, vless_data: dict) -> dict:
    """
    Применяет данные VLESS к шаблону
    
    Args:
        template: Шаблон конфигурации
        vless_data: Данные VLESS
        
    Returns:
        Заполненный шаблон
    """
    params = vless_data['params']
    
    # Подготавливаем данные для замены
    replacements = {
        'address': vless_data['server'],
        'port': str(vless_data['port']),
        'id': vless_data['uuid'],
        'tag': vless_data.get('fragment', 'proxy')
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


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description='Конвертер VLESS URL в формат конфигурации Xray-core',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Примеры использования:
  python vless_to_xray.py                                      # Интерактивный режим
  python vless_to_xray.py "vless://..."                       # Конвертация URL
  python vless_to_xray.py --template openwrt-reverse "vless://..." # Использование шаблона
  python vless_to_xray.py --output config.json "vless://..."  # Сохранение в файл
  python vless_to_xray.py --list-templates                    # Список доступных шаблонов
        '''
    )
    
    parser.add_argument('url', nargs='?', help='VLESS URL для конвертации')
    parser.add_argument('--template', '-t', help='Имя шаблона для использования')
    parser.add_argument('--output', '-o', help='Файл для сохранения результата')
    parser.add_argument('--list-templates', action='store_true', help='Показать доступные шаблоны')
    
    args = parser.parse_args()
    
    # Показать доступные шаблоны
    if args.list_templates:
        templates = get_available_templates()
        print("Доступные шаблоны:")
        for name, path in templates.items():
            print(f"  {name} - {path}")
        return
    
    # Определяем VLESS URL и тег
    vless_url = None
    tag = None
    
    if args.url:
        # Режим с аргументом командной строки
        vless_url = args.url
        # Если используется шаблон, тег не нужен (он будет из URL или по умолчанию)
        if not args.template:
            tag = None
    else:
        # Интерактивный режим
        print("Конвертер VLESS в формат Xray-core")
        print("=" * 40)
        
        # Показываем доступные шаблоны
        templates = get_available_templates()
        if templates:
            print("Доступные шаблоны:")
            for name, path in templates.items():
                print(f"  {name} - {path}")
            print()
        
        # Шаг 1: Запрашиваем название шаблона (необязательно)
        available_templates_str = ', '.join(templates.keys()) if templates else "нет"
        template_name = input(f"Введите название шаблона ({available_templates_str}) или нажмите Enter для пропуска: ").strip()
        
        selected_template = None
        if template_name:
            if not templates:
                print("Ошибка: Шаблоны не найдены.")
                sys.exit(1)
            
            if template_name not in templates:
                print(f"Ошибка: Неверное название шаблона '{template_name}'. Доступные: {', '.join(templates.keys())}")
                sys.exit(1)
            
            selected_template = template_name
        
        # Шаг 2: Запрашиваем VLESS URL
        vless_url = input("Введите VLESS URL: ").strip()
        if not vless_url:
            print("Ошибка: VLESS URL не может быть пустым")
            sys.exit(1)
        
        # Шаг 3: Запрашиваем тег если не используется шаблон
        if not selected_template:
            tag = input("Введите тег для конфигурации: ").strip()
            if not tag:
                print("Ошибка: Тег не может быть пустым")
                sys.exit(1)
        else:
            tag = None  # Тег будет определен из URL или по умолчанию
        
        # Шаг 4: Запрашиваем файл для сохранения (необязательно)
        output_file = input("Введите название файла для сохранения или нажмите Enter для вывода на экран: ").strip()
        
        # Применяем выбранный шаблон и файл сохранения
        args.template = selected_template
        args.output = output_file if output_file else None
    
    try:
        # Парсим VLESS URL
        vless_data = parse_vless_url(vless_url)
        
        # Определяем финальный тег
        if args.template:
            # При использовании шаблона тег берется из URL или по умолчанию
            final_tag = vless_data.get('fragment', 'proxy')
        else:
            # Используем переданный тег или из URL
            final_tag = tag if tag else vless_data.get('fragment', 'proxy')
        
        # Создаем конфигурацию
        if args.template:
            # Используем шаблон
            template = load_template(args.template)
            config = apply_template(template, vless_data)
        else:
            # Стандартная конвертация
            config = create_xray_config(vless_data, final_tag)
        
        # Сохраняем или выводим результат
        if args.output:
            save_to_file(config, args.output)
        else:
            print(json.dumps(config, indent=4, ensure_ascii=False))
        
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 