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


def create_xray_config(vless_data: dict) -> dict:
    """
    Создает конфигурацию Xray на основе данных VLESS
    
    Args:
        vless_data: Словарь с данными VLESS
        
    Returns:
        Словарь конфигурации Xray
    """
    params = vless_data['params']
    
    # Базовая конфигурация
    config = {
        "type": "vless",
        "tag": "proxy",
        "server": vless_data['server'],
        "server_port": vless_data['port'],
        "uuid": vless_data['uuid'],
        "encryption": "none",  # VLESS всегда использует none
        "flow": "",
        "packet_encoding": "",
        "domain_strategy": ""
    }
    
    # Добавляем flow если указан
    if 'flow' in params:
        config['flow'] = params['flow']
    
    # Настраиваем TLS
    if params.get('security') == 'tls' or params.get('security') == 'reality':
        tls_config = {
            "enabled": True,
            "alpn": [],
            "utls": {
                "enabled": True,
                "fingerprint": "chrome"
            }
        }
        
        # Добавляем ALPN
        if 'alpn' in params:
            alpn_values = params['alpn'].split(',')
            tls_config['alpn'] = [value.strip() for value in alpn_values]
        
        # Настраиваем fingerprint
        if 'fp' in params:
            tls_config['utls']['fingerprint'] = params['fp']
        
        config['tls'] = tls_config
    
    # Настраиваем тип соединения
    if 'type' in params:
        config['network'] = params['type']
    
    # Добавляем поддержку REALITY
    if params.get('security') == 'reality':
        if 'pbk' in params:
            if 'tls' not in config:
                config['tls'] = {}
            config['tls']['reality'] = {
                "enabled": True,
                "public_key": params['pbk']
            }
            if 'sni' in params:
                config['tls']['reality']['server_name'] = params['sni']
            if 'fp' in params:
                config['tls']['reality']['fingerprint'] = params['fp']
            if 'spx' in params:
                config['tls']['reality']['spider_x'] = params['spx']
    
    return config


def main():
    """Основная функция"""
    if len(sys.argv) != 2:
        print("Использование: python vless_to_xray.py \"vless://...\"")
        print("Пример: python vless_to_xray.py \"vless://b81e68ca-0236-4f30-9942-18c93a1a29fc@dropbit.pro:443?security=tls&alpn=http/1.1&fp=chrome&type=tcp&flow=xtls-rprx-vision&encryption=none#Hidden%20router-main\"")
        sys.exit(1)
    
    vless_url = sys.argv[1]
    
    try:
        # Парсим VLESS URL
        vless_data = parse_vless_url(vless_url)
        
        # Создаем конфигурацию Xray
        xray_config = create_xray_config(vless_data)
        
        # Выводим результат в формате JSON
        print(json.dumps(xray_config, indent=12, ensure_ascii=False))
        
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 