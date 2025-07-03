# VLESS to Xray Converter

Скрипт для конвертации VLESS конфигурации в формат Xray-core с поддержкой шаблонов.

## Описание

Этот скрипт принимает строку конфигурации VLESS (включая TLS/REALITY) и преобразует её в JSON конфигурацию в формате Xray-core. Поддерживает как простую конвертацию, так и применение готовых шаблонов для специфических конфигураций.

## Возможности

- ✅ Конвертация VLESS URL в формат Xray-core
- ✅ Поддержка TLS и REALITY
- ✅ Интерактивный режим
- ✅ Система шаблонов для готовых конфигураций
- ✅ Сохранение результата в файл
- ✅ Поддержка различных типов соединений (TCP, WebSocket, gRPC)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/SoaQa/vless-to-xray-converter.git
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

## Структура проекта

```
vless-to-xray-converter/
├── main.py                      # Точка входа в приложение
├── vless_converter/             # Основной пакет
│   ├── __init__.py             # Инициализация пакета
│   ├── parser.py               # Парсинг VLESS URL
│   ├── generator.py            # Генерация конфигураций Xray
│   ├── templates.py            # Работа с шаблонами
│   └── utils.py                # Вспомогательные функции
├── templates/                   # Шаблоны конфигураций
│   └── openwrt-reverse-proxy.json
├── requirements.txt             # Зависимости Python
└── README.md                   # Документация
```

### Модули пакета

- **`parser.py`** - Отвечает за разбор VLESS URL и извлечение параметров
- **`generator.py`** - Создает стандартные конфигурации Xray-core
- **`templates.py`** - Управляет загрузкой и применением шаблонов
- **`utils.py`** - Содержит утилиты для сохранения файлов и форматирования

## Использование

### Основные режимы

1. **Интерактивный режим** (рекомендуется):
```bash
python main.py
```
*В интерактивном режиме скрипт пошагово запросит:*
- *Номер или название шаблона (необязательно - можно пропустить)*
- *VLESS URL для конвертации*
- *Тег конфигурации (если шаблон не используется)*
- *Название файла для сохранения (необязательно - можно пропустить)*

2. **Режим с аргументами**:
```bash
python main.py "vless://..."
```

3. **Использование шаблонов**:
```bash
python main.py --template openwrt-reverse "vless://..."
python main.py --template 1 "vless://..."  # По номеру
```

4. **Сохранение в файл**:
```bash
python main.py --output config.json "vless://..."
```

### Флаги команды

- `--template`, `-t` - использовать шаблон по имени или номеру (см. список ниже)
- `--output`, `-o` - сохранить результат в файл
- `--list-templates` - показать доступные шаблоны с номерами
- `--help`, `-h` - показать справку

### Примеры

#### Интерактивный режим
```bash
python main.py
```
*Пример сессии:*
```
Конвертер VLESS в формат Xray-core
========================================
Доступные шаблоны:
  1. openwrt-reverse - templates/openwrt-reverse-proxy.json

Введите номер или название шаблона (1 (openwrt-reverse)) или нажмите Enter для пропуска: 1
Введите VLESS URL: vless://uuid@server:port?security=reality&pbk=key&sni=domain.com&sid=123&spx=/#tag
Введите название файла для сохранения или нажмите Enter для вывода на экран: config.json
Конфигурация сохранена в файл: config.json
```

#### Простая конвертация
```bash
python main.py "vless://uuid@server:port?security=reality&pbk=key&sni=domain.com&sid=123&spx=/#tag"
```

#### Использование шаблона OpenWRT reverse proxy
```bash
# По имени
python main.py --template openwrt-reverse "vless://uuid@server:port?security=reality&pbk=key&sni=domain.com&sid=123&spx=/#tag"

# По номеру
python main.py --template 1 "vless://uuid@server:port?security=reality&pbk=key&sni=domain.com&sid=123&spx=/#tag"
```

#### Сохранение в файл
```bash
python main.py --output my-config.json "vless://uuid@server:port?security=reality&pbk=key&sni=domain.com&sid=123&spx=/#tag"
```

#### Просмотр доступных шаблонов
```bash
python main.py --list-templates
```

## Результат

### Обычная конвертация
Скрипт выведет JSON конфигурацию в формате Xray-core:

```json
{
    "protocol": "vless",
    "settings": {
        "vnext": [
            {
                "address": "server.example.com",
                "port": 443,
                "users": [
                    {
                        "id": "uuid",
                        "encryption": "none"
                    }
                ]
            }
        ]
    },
    "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
            "publicKey": "publicKey",
            "serverName": "domain.com",
            "fingerprint": "chrome",
            "shortId": "123",
            "spiderX": "/"
        }
    },
    "tag": "proxy"
}
```

### Конвертация с шаблоном
При использовании шаблона `openwrt-reverse` получается полная конфигурация для OpenWRT reverse proxy:

```json
{
    "log": {
        "loglevel": "warning"
    },
    "outbounds": [
        {
            "tag": "out",
            "protocol": "freedom",
            "settings": {
                "redirect": "127.0.0.1:80"
            }
        },
        {
            "protocol": "vless",
            "settings": {
                "vnext": [...]
            },
            "streamSettings": {...},
            "tag": "proxy"
        }
    ],
    "routing": {...},
    "reverse": {...}
}
```

## Шаблоны

### Доступные шаблоны

- `openwrt-reverse` - полная конфигурация для OpenWRT reverse proxy

### Создание собственных шаблонов

1. Создайте JSON файл в директории `templates/`
2. Используйте плейсхолдеры в двойных фигурных скобках:
   - `{{address}}` - адрес сервера
   - `{{port}}` - порт
   - `{{id}}` - UUID
   - `{{tag}}` - тег конфигурации
   - `{{publicKey}}` - публичный ключ для Reality
   - `{{serverName}}` - имя сервера для Reality
   - `{{fingerprint}}` - отпечаток TLS
   - `{{shortId}}` - короткий ID для Reality
   - `{{spiderX}}` - путь для Reality

3. Добавьте шаблон в функцию `get_available_templates()` в коде

## Поддерживаемые параметры VLESS

- `security`: tls, reality
- `alpn`: протоколы ALPN (разделенные запятыми)
- `fp`: fingerprint для TLS
- `type`: тип соединения (tcp, ws, grpc)
- `flow`: flow для XTLS
- `encryption`: метод шифрования (всегда none для VLESS)
- `pbk`: публичный ключ для Reality
- `sni`: имя сервера для TLS/Reality
- `sid`: короткий ID для Reality
- `spx`: путь для Reality
- `host`: заголовок Host для WebSocket/HTTP
- `path`: путь для WebSocket/HTTP
- `serviceName`: имя сервиса для gRPC
- `mode`: режим gRPC (gun/multi)

## Требования

- Python 3.7+
- Все необходимые модули входят в стандартную библиотеку Python

## Лицензия

MIT 