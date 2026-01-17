#!/usr/bin/env python3
"""
Streamlit интерфейс для TblMaker
"""

import streamlit as st
import json
from tblmaker import parse_text, generate_html, load_template

# Конфигурация страницы
st.set_page_config(
    page_title="TblMaker - Creatium Table Generator",
    page_icon="🏒",
    layout="centered"
)

# Заголовок
st.title("🏒 TblMaker")
st.markdown("Конвертер данных хоккейной команды в таблицу Creatium")

# Секции ввода
st.header("1. Введите данные")

# Два способа ввода
input_method = st.radio(
    "Способ ввода данных:",
    ["Загрузить файл", "Вставить текст"],
    horizontal=True
)

raw_text = None

if input_method == "Загрузить файл":
    uploaded_file = st.file_uploader(
        "Выберите .txt файл",
        type=['txt'],
        help="Файл с табулированными данными"
    )
    if uploaded_file:
        raw_text = uploaded_file.getvalue().decode('utf-8')
        st.success("✅ Файл загружен!")
else:
    raw_text = st.text_area(
        "Вставьте данные:",
        height=200,
        placeholder="Номер\tФамилия, имя\tАмплуа\tДата рождения\tГражданство\n35\tКульбаков Иван\tвратарь\t18.09.1996\tБеларусь\n...",
        help="Вставьте данные из Excel или текстового редактора"
    )

# Парсинг и генерация
if raw_text:
    try:
        rows, coach = parse_text(raw_text)

        # Статистика
        st.header("2. Статистика")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Игроков", len(rows))
        with col2:
            st.metric("Тренер", coach['name'] if coach else "Не указан")

        # Preview данных
        with st.expander("👁️ Посмотреть загруженные данные"):
            st.dataframe(rows, use_container_width=True)

        # Генерация HTML
        html_table = generate_html(rows, coach)

        # Preview таблицы
        st.header("3. Предпросмотр таблицы")
        st.markdown(html_table, unsafe_allow_html=True)

        # Генерация JSON
        template = load_template('template.json')
        template['data']['embeds']['cont']['html']['children'][0]['code'] = html_table
        json_output = json.dumps(template, ensure_ascii=False, separators=(',', ':'))

        # Скачивание
        st.header("4. Скачать результат")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Скачать JSON",
                data=json_output,
                file_name="creatium_table.json",
                mime="application/json",
                use_container_width=True
            )
        with col2:
            # Показать JSON для копирования
            with st.popover("📋 Скопировать JSON", use_container_width=True):
                st.text_area(
                    "JSON для Creatium (нажмите Ctrl+C чтобы скопировать):",
                    value=json_output,
                    height=300,
                    key="json_copy_area",
                    label_visibility="collapsed"
                )
                st.info("💡 Нажмите Ctrl+C (или Cmd+C на Mac) чтобы скопировать")

    except Exception as e:
        st.error(f"❌ Ошибка при обработке данных: {e}")
        st.info("💡 Проверьте формат данных. Должны быть табы между колонками.")

# Инструкция
st.divider()
with st.expander("📖 Инструкция по формату данных"):
    st.markdown("""
    ### Формат входных данных:

    **Первая строка** - заголовки (обязательно):
    ```
    Номер	Фамилия, имя	Амплуа	Дата рождения	Гражданство
    ```

    **Данные** - разделены табуляцией (TAB):
    ```
    35	Кульбаков Иван	вратарь	18.09.1996	Беларусь
    72	Костин Денис	вратарь	21.06.1995	Россия
    ```

    **Тренер** (опционально) в последней строке:
    ```
    Главный тренер: Исаков Алексей
    ```

    ### Как скопировать из Excel:
    1. Выделите таблицу в Excel
    2. Ctrl+C (копировать)
    3. Вставьте в поле выше - табы сохранятся автоматически
    """)
