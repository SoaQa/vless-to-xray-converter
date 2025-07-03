"""
Модуль для генерации конфигураций Xray

Содержит функции для создания конфигураций в формате Xray-core.
"""


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
    
    # Определяем тег: переданный параметр, fragment из URL, или 'reverse-proxy' по умолчанию
    if tag:
        config_tag = tag
    elif vless_data.get('fragment'):
        config_tag = vless_data['fragment']
    else:
        config_tag = 'reverse-proxy'
    
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