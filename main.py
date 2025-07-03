#!/usr/bin/env python3
"""
VLESS to Xray Converter

Главный файл для запуска приложения.
Использование: python main.py "vless://..."
"""

import sys
import argparse
from vless_converter import (
    parse_vless_url,
    create_xray_config,
    get_available_templates,
    load_template,
    apply_template,
    save_to_file,
    display_templates_with_numbers,
    resolve_template_name
)
from vless_converter.utils import format_json_output


def main():
    """Основная функция приложения"""
    parser = argparse.ArgumentParser(
        description='Конвертер VLESS URL в формат конфигурации Xray-core',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Примеры использования:
  python main.py                                      # Интерактивный режим
  python main.py "vless://..."                        # Конвертация URL
  python main.py --template openwrt-reverse "vless://..." # Использование шаблона
  python main.py --template 1 "vless://..."          # Использование шаблона по номеру
  python main.py --output config.json "vless://..."  # Сохранение в файл
  python main.py --list-templates                     # Список доступных шаблонов
        '''
    )
    
    parser.add_argument('url', nargs='?', help='VLESS URL для конвертации')
    parser.add_argument('--template', '-t', help='Имя или номер шаблона для использования')
    parser.add_argument('--output', '-o', help='Файл для сохранения результата')
    parser.add_argument('--list-templates', action='store_true', help='Показать доступные шаблоны')
    
    args = parser.parse_args()
    
    # Показать доступные шаблоны
    if args.list_templates:
        display_templates_with_numbers()
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
            # Преобразуем номер в имя шаблона если нужно
            try:
                args.template = resolve_template_name(args.template)
            except ValueError as e:
                print(f"Ошибка: {e}")
                sys.exit(1)
    else:
        # Интерактивный режим
        vless_url, tag = run_interactive_mode(args)
    
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
            print(format_json_output(config))
        
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


def run_interactive_mode(args):
    """
    Запускает интерактивный режим для получения данных от пользователя
    
    Args:
        args: Аргументы командной строки
        
    Returns:
        Tuple[str, str]: VLESS URL и тег
    """
    print("Конвертер VLESS в формат Xray-core")
    print("=" * 40)
    
    # Показываем доступные шаблоны с номерами
    numbered_templates = display_templates_with_numbers()
    
    # Шаг 1: Запрашиваем название/номер шаблона (необязательно)
    if numbered_templates:
        available_options = []
        for num, name in numbered_templates.items():
            available_options.append(f"{num} ({name})")
        available_str = ', '.join(available_options)
    else:
        available_str = "нет"
    
    template_input = input(f"Введите номер или название шаблона ({available_str}) или нажмите Enter для пропуска: ").strip()
    
    selected_template = None
    if template_input:
        try:
            selected_template = resolve_template_name(template_input)
        except ValueError as e:
            print(f"Ошибка: {e}")
            sys.exit(1)
    
    # Шаг 2: Запрашиваем VLESS URL
    vless_url = input("Введите VLESS URL: ").strip()
    if not vless_url:
        print("Ошибка: VLESS URL не может быть пустым")
        sys.exit(1)
    
    # Шаг 3: Запрашиваем тег если не используется шаблон
    tag = None
    if not selected_template:
        tag = input("Введите тег для конфигурации: ").strip()
        if not tag:
            print("Ошибка: Тег не может быть пустым")
            sys.exit(1)
    
    # Шаг 4: Запрашиваем файл для сохранения (необязательно)
    output_file = input("Введите название файла для сохранения или нажмите Enter для вывода на экран: ").strip()
    
    # Применяем выбранный шаблон и файл сохранения
    args.template = selected_template
    args.output = output_file if output_file else None
    
    return vless_url, tag


if __name__ == "__main__":
    main() 