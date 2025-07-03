# VLESS to Xray Converter

Утилита для конвертации VLESS URL в конфигурацию Xray-core. Поддерживает различные типы соединений (TLS, Reality, WebSocket, gRPC, TCP) и систему шаблонов.

## Возможности

- Конвертация VLESS URL в формат Xray-core
- Поддержка различных типов соединений (TLS, Reality, WebSocket, gRPC, TCP)
- Система шаблонов для различных сценариев использования
- Интерактивный режим для удобного использования
- Сохранение конфигураций в файл
- Поддержка пользовательских тегов

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

### Интерактивный режим

Самый простой способ использования - без аргументов:

```bash
python main.py
```

В интерактивном режиме программа запросит:
1. VLESS URL
2. Тег для конфигурации (по умолчанию: reverse-proxy)
3. Шаблон (опционально)
4. Файл для сохранения (опционально)

### Командная строка

```bash
# Базовое использование
python main.py vless://... --tag my-server

# Использование шаблона
python main.py vless://... --template openwrt-reverse --tag my-server

# Сохранение в файл
python main.py vless://... --output config.json

# Список доступных шаблонов
python main.py --list-templates
```

### Аргументы командной строки

- `vless_url` - VLESS URL для конвертации
- `--tag, -g` - Тег для конфигурации (по умолчанию: reverse-proxy)
- `--template, -t` - Использовать шаблон (номер или имя)
- `--output, -o` - Сохранить результат в файл
- `--list-templates` - Показать список доступных шаблонов

## Теги

Во всех режимах работы программа запрашивает тег для конфигурации:

- **По умолчанию**: `reverse-proxy`
- **Из URL**: если в VLESS URL есть fragment (часть после #), он используется как тег
- **Пользовательский**: можно указать любой тег через параметр `--tag` или в интерактивном режиме
- **При использовании шаблонов**: тег применяется как в конфигурации VLESS, так и в правилах маршрутизации

## Шаблоны

Программа поддерживает систему шаблонов для различных сценариев использования.

### Доступные шаблоны

- `openwrt-reverse-proxy` - Конфигурация для OpenWRT с обратным прокси

### Использование шаблонов

```bash
# По номеру
python main.py vless://... --template 1

# По имени
python main.py vless://... --template openwrt-reverse

# Показать доступные шаблоны
python main.py --list-templates
```

### Создание собственных шаблонов

Шаблоны хранятся в папке `templates/` в формате JSON. Можно использовать следующие плейсхолдеры:

- `{{address}}` - Адрес сервера
- `{{port}}` - Порт
- `{{id}}` - UUID пользователя
- `{{tag}}` - Тег конфигурации
- `{{publicKey}}` - Публичный ключ (для Reality)
- `{{serverName}}` - Имя сервера (SNI)
- `{{fingerprint}}` - Отпечаток TLS
- `{{shortId}}` - Короткий ID (для Reality)
- `{{spiderX}}` - Spider X (для Reality)

## Примеры

### Базовая конвертация

```bash
python main.py "vless://uuid@server.com:443?security=tls&type=tcp#my-server"
```

### Использование шаблона

```bash
python main.py "vless://uuid@server.com:443?security=reality&type=tcp&pbk=key&sni=example.com#my-server" --template openwrt-reverse
```

### Интерактивный режим

```bash
python main.py
# Введите VLESS URL: vless://uuid@server.com:443?security=tls&type=tcp#my-server
# Введите тег для конфигурации (по умолчанию: reverse-proxy): my-server
# Введите имя шаблона (номер или имя, или Enter для пропуска): 1
# Введите имя файла для сохранения (или Enter для пропуска): config.json
```

## Поддерживаемые типы соединений

- **TLS**: Стандартное TLS соединение
- **Reality**: Новый протокол от Xray
- **WebSocket**: HTTP/WebSocket соединение
- **gRPC**: gRPC соединение
- **TCP**: Прямое TCP соединение

## Лицензия

MIT 