#!/usr/bin/env python3
"""
VLESS to Xray Converter

Главный файл для запуска приложения.
Использование: python main.py "vless://..."
"""

import sys
import argparse
import json
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
    """Основная функция программы"""
    parser = argparse.ArgumentParser(
        description='Конвертер VLESS URL в конфигурацию Xray-core',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Примеры использования:
        
  Интерактивный режим:
    python main.py
    
  Базовое использование:
    python main.py vless://... --tag my-server
    
  Использование шаблона:
    python main.py vless://... --template openwrt-reverse
    
  Список доступных шаблонов:
    python main.py --list-templates
        '''
    )
    
    parser.add_argument('vless_url', nargs='?', help='VLESS URL для конвертации')
    parser.add_argument('--tag', '-g', help='Тег для конфигурации (по умолчанию: reverse-proxy)')
    parser.add_argument('--template', '-t', help='Использовать шаблон (номер или имя)')
    parser.add_argument('--output', '-o', help='Сохранить результат в файл')
    parser.add_argument('--list-templates', action='store_true', help='Показать список доступных шаблонов')
    
    args = parser.parse_args()
    
    if args.list_templates:
        display_templates_with_numbers()
        return
    
    # Интерактивный режим
    if not args.vless_url:
        print("Интерактивный режим")
        print("=" * 50)
        
        # Получаем URL
        vless_url = input("Введите VLESS URL: ").strip()
        if not vless_url:
            print("Ошибка: URL не может быть пустым")
            return
        
        # Парсим URL
        try:
            vless_data = parse_vless_url(vless_url)
        except Exception as e:
            print(f"Ошибка парсинга URL: {e}")
            return
        
        # Запрашиваем тег (всегда)
        tag = input("Введите тег для конфигурации (по умолчанию: reverse-proxy): ").strip()
        if not tag:
            tag = 'reverse-proxy'
        
        display_templates_with_numbers()
        
        # Выбираем шаблон
        template_name = input("Введите имя шаблона (номер или имя, или Enter для пропуска): ").strip()
        if template_name:
            template_path = resolve_template_name(template_name)
            if not template_path:
                print(f"Ошибка: Шаблон '{template_name}' не найден")
                return
            
            template = load_template(template_path)
            if not template:
                print(f"Ошибка: Не удалось загрузить шаблон '{template_name}'")
                return
            
                    # Применяем шаблон с пользовательским тегом
        config = apply_template(template, vless_data, tag)
    else:
        # Генерируем базовую конфигурацию
        config = create_xray_config(vless_data, tag)
    
    # Сохраняем в файл
    output_file = input("\nВведите имя файла для сохранения (или Enter для пропуска): ").strip()
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"Конфигурация сохранена в файл: {output_file}")
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")
    else:
        # Выводим результат только если файл не указан
        print("\nСгенерированная конфигурация:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
    
    return
    
    # Режим с аргументами
    try:
        vless_data = parse_vless_url(args.vless_url)
    except Exception as e:
        print(f"Ошибка парсинга URL: {e}")
        return
    
    # Запрашиваем тег если не задан
    if not args.tag:
        tag = input("Введите тег для конфигурации (по умолчанию: reverse-proxy): ").strip()
        if not tag:
            tag = 'reverse-proxy'
    else:
        tag = args.tag
    
    # Используем шаблон или генерируем базовую конфигурацию
    if args.template:
        template_path = resolve_template_name(args.template)
        if not template_path:
            print(f"Ошибка: Шаблон '{args.template}' не найден")
            return
        
        template = load_template(template_path)
        if not template:
            print(f"Ошибка: Не удалось загрузить шаблон '{args.template}'")
            return
        
        # Применяем шаблон с пользовательским тегом
        config = apply_template(template, vless_data, tag)
    else:
        # Генерируем базовую конфигурацию
        config = create_xray_config(vless_data, tag)
    
    # Выводим результат
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    # Сохраняем в файл
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"\nКонфигурация сохранена в файл: {args.output}")
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")


if __name__ == "__main__":
    main() 