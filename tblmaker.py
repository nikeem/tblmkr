#!/usr/bin/env python3
"""
Table Maker - конвертирует текстовые данные в таблицу Creatium
"""

import json
import re


def parse_input(filepath: str) -> tuple[list[dict], dict | None]:
    """
    Парсит входной txt файл в список словарей.

    Формат: первая строка - заголовки, далее - данные через табы.
    Последняя строка может быть "Главный тренер: Имя"
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    return parse_text(text)


def parse_text(text: str) -> tuple[list[dict], dict | None]:
    """
    Парсит текст из памяти (аналогично parse_input, но для строковой переменной).

    Args:
        text: Текст с табулированными данными

    Returns:
        (rows, coach) - список словарей с игроками и опционально словарь тренера
    """
    lines = text.strip().split('\n')

    # Первая строка - заголовки (не используем, но можем проверить)
    headers = lines[0].split('\t')

    rows = []
    coach = None

    for line in lines[1:]:
        if not line.strip():
            continue

        # Проверяем на тренера
        if line.startswith('Главный тренер:'):
            coach_name = line.replace('Главный тренер:', '').strip()
            coach = {'name': coach_name}
            continue

        # Парсим обычную строку (фильтруем пустые элементы от множественных табов)
        parts = [p.strip() for p in line.split('\t') if p.strip()]
        if len(parts) >= 5:
            rows.append({
                'number': parts[0],
                'name': parts[1],
                'role': parts[2],
                'birth': parts[3],
                'country': parts[4]
            })

    return rows, coach


def abbreviate_role(role: str) -> str:
    """Сокращает амплуа."""
    role_lower = role.lower()
    if 'вратарь' in role_lower:
        return 'вр.'
    elif 'защитник' in role_lower:
        return 'защ.'
    elif 'нападающий' in role_lower:
        return 'нап.'
    return role


def generate_html(rows: list[dict], coach: dict | None = None) -> str:
    """
    Генерирует HTML таблицу для Creatium.

    Ширины колонок: 3.75%, 37.625%, 12.7937%, 26.1958%, 19.5542%
    """
    widths = ['3.75%', '37.625%', '12.7937%', '26.1958%', '19.5542%']

    html_parts = ['<table style="width: 100%;"><tbody>']

    # Заголовок
    html_parts.append('<tr>')
    headers = ['№', 'Фамилия, имя', 'Амплуа', 'Дата рождения', 'Гражданство']
    for i, header in enumerate(headers):
        html_parts.append(f'<td style="text-align: center; width: {widths[i]};">{header}<br></td>')
    html_parts.append('</tr>')

    # Строки с игроками
    for row in rows:
        html_parts.append('<tr>')
        role_abbr = abbreviate_role(row['role'])

        cells = [
            row['number'],
            row['name'],
            role_abbr,
            row['birth'],
            row['country']
        ]

        for i, cell in enumerate(cells):
            html_parts.append(
                f'<td style="text-align: center; vertical-align: middle; width: {widths[i]};">'
                f'{cell}<br></td>'
            )
        html_parts.append('</tr>')

    # Тренер (если есть)
    if coach:
        html_parts.append('<tr>')
        # Пустой номер, имя, гл.тр., пустая дата, пустая страна
        html_parts.append(f'<td style="text-align: center; vertical-align: middle; width: {widths[0]};"><br></td>')
        html_parts.append(f'<td style="text-align: center; vertical-align: middle; width: {widths[1]};">{coach["name"]}<br></td>')
        html_parts.append(f'<td style="text-align: center; vertical-align: middle; width: {widths[2]};">гл.тр.<br></td>')
        html_parts.append(f'<td style="text-align: center; vertical-align: middle; width: {widths[3]};"><br></td>')
        html_parts.append(f'<td style="text-align: center; vertical-align: middle; width: {widths[4]};"><br></td>')
        html_parts.append('</tr>')

    html_parts.append('</tbody></table>')

    return ''.join(html_parts)


def load_template(filepath: str = 'template.json') -> dict:
    """Загружает JSON шаблон Creatium."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: dict, filepath: str):
    """Сохраняет JSON в файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))


def main():
    """Главная функция."""
    # Парсим входной файл
    rows, coach = parse_input('in.txt')

    # Генерируем HTML таблицу
    html_table = generate_html(rows, coach)

    # Загружаем шаблон
    template = load_template('template.json')

    # Вставляем HTML в шаблон
    # Путь: embeds -> cont -> html -> children -> [0] -> code
    template['data']['embeds']['cont']['html']['datamix']['ast'] = '4.4'
    template['data']['embeds']['cont']['html']['children'][0]['code'] = html_table

    # Сохраняем результат
    save_json(template, 'out.txt')

    print(f'Готово! Обработано {len(rows)} игроков' + (f' + тренер {coach["name"]}' if coach else ''))


if __name__ == '__main__':
    main()
