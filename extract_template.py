#!/usr/bin/env python3
"""
Извлекает шаблон из out.txt для последующего использования.
"""

import json

# Читаем out.txt
with open('out.txt', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Очищаем HTML код таблицы
data['data']['embeds']['cont']['html']['children'][0]['code'] = 'PLACEHOLDER_HTML'

# Генерируем новый UID
import uuid
data['uid'] = str(uuid.uuid4()).replace('-', '')[:24]

# Сохраняем как template.json
with open('template.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Шаблон сохранён в template.json')
