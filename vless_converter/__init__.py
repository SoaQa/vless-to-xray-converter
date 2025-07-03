"""
VLESS to Xray Converter Package

Пакет для конвертации VLESS конфигураций в формат Xray-core.
"""

from .parser import parse_vless_url
from .generator import create_xray_config
from .templates import get_available_templates, load_template, apply_template, display_templates_with_numbers, resolve_template_name
from .utils import save_to_file

__version__ = "1.0.0"
__author__ = "SoaQa"

__all__ = [
    'parse_vless_url',
    'create_xray_config',
    'get_available_templates',
    'load_template',
    'apply_template',
    'display_templates_with_numbers',
    'resolve_template_name',
    'save_to_file'
] 