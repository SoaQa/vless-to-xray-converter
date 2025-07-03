# VLESS to Xray Converter

Скрипт для конвертации VLESS конфигурации в формат Xray.

## Описание

Этот скрипт принимает строку конфигурации VLESS (включая TLS/REALITY) и преобразует её в JSON конфигурацию, которую можно добавить в секцию `inbounds` или `outbounds` файла конфигурации Xray.

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd vless-to-xray-converter
```

2. Создайте виртуальное окружение (опционально):
```bash
python -m venv venv
# На Windows:
venv\Scripts\activate
# На Linux/Mac:
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

```bash
python vless_to_xray.py "vless://..."
```

### Пример

```bash
python vless_to_xray.py "vless://<UUID>@<SERVER>:443?security=tls&alpn=http/1.1&fp=chrome&type=tcp&flow=xtls-rprx-vision&encryption=none#Hidden%20router-main"
```

### Результат

Скрипт выведет JSON конфигурацию в формате:

```json
{
            "domain_strategy": "",
            "flow": "xtls-rprx-vision",
            "packet_encoding": "",
            "server": "<SERVER>",
            "server_port": 443,
            "tag": "proxy",
            "tls": {
                "alpn": [
                    "http/1.1"
                ],
                "enabled": true,
                "utls": {
                    "enabled": true,
                    "fingerprint": "chrome"
                }
            },
            "type": "vless",
            "uuid": "<UUID>"
        }
```

## Поддерживаемые параметры

- `security`: tls, reality
- `alpn`: протоколы ALPN (разделенные запятыми)
- `fp`: fingerprint для uTLS
- `type`: тип соединения (tcp, ws, grpc и др.)
- `flow`: flow для XTLS
- `encryption`: метод шифрования (всегда none для VLESS)

## Требования

- Python 3.7+
- Все необходимые модули входят в стандартную библиотеку Python

## Лицензия

MIT 