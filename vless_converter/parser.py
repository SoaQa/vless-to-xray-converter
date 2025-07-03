"""
Модуль для парсинга VLESS URL

Содержит функции для разбора VLESS конфигураций.
"""

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