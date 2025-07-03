#!/usr/bin/env python3
"""
Скрипт для конвертации VLESS конфигурации в формат Xray
Использование: python vless_to_xray.py "vless://..."
"""

import sys
import json
import urllib.parse
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


def main():
    """Основная функция"""
    if len(sys.argv) == 1:
        # Интерактивный режим - запрашиваем VLESS URL и тег
        print("Конвертер VLESS в формат Xray-core")
        print("=" * 40)
        
        # Шаг 1: Запрашиваем VLESS URL
        vless_url = input("Введите VLESS URL: ").strip()
        if not vless_url:
            print("Ошибка: VLESS URL не может быть пустым")
            sys.exit(1)
        
        # Шаг 2: Запрашиваем тег
        tag = input("Введите тег для конфигурации: ").strip()
        if not tag:
            print("Ошибка: Тег не может быть пустым")
            sys.exit(1)
            
    elif len(sys.argv) == 2:
        # Режим с аргументом командной строки
        vless_url = sys.argv[1]
        tag = None  # Тег будет определен автоматически
        
    else:
        print("Использование: python vless_to_xray.py [\"vless://...\"]")
        print("Скрипт конвертирует VLESS URL в формат конфигурации Xray-core")
        print("Если запустить без аргументов, будет запрошен VLESS URL и тег")
        sys.exit(1)
    
    try:
        # Парсим VLESS URL
        vless_data = parse_vless_url(vless_url)
        
        # Создаем конфигурацию Xray
        xray_config = create_xray_config(vless_data, tag)
        
        # Выводим результат в формате JSON
        print(json.dumps(xray_config, indent=4, ensure_ascii=False))
        
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 