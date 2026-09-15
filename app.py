"""
Science Paper Analyzer — Streamlit Web Application
Анализ научных статей на достоверность
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzer import PaperAnalyzer, SOURCE_DISPLAY

# Конфигурация страницы
st.set_page_config(
    page_title="Science Paper Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Кэш для результатов в сессии
if "results_df" not in st.session_state:
    st.session_state.results_df = None
if "query" not in st.session_state:
    st.session_state.query = ""
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False


def main():
    # --- HEADER ---
    st.title("🔬 Science Paper Analyzer")
    st.markdown(
        """
        Система для сбора и верификации научных статей.
        Анализирует публикации из **10+ научных источников** и определяет
        вероятность того, что статья является **фейковой/недостоверной**.
        """
    )

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Параметры анализа")
        
        query = st.text_input(
            "📝 Тема поиска:",
            value=st.session_state.query,
            placeholder="Например: 'collapse of language models' или 'NLP filtering'",
            help="Введите ключевые слова для поиска научных статей"
        )

        col1, col2 = st.columns(2)
        with col1:
            max_sources = st.slider(
                "Источники",
                min_value=1, max_value=10, value=10,
                help="Сколько из 10 доступных источников использовать"
            )
        with col2:
            max_per_source = st.slider(
                "Статей/источник",
                min_value=1, max_value=10, value=5,
                help="Максимум статей с каждого источника"
            )

        # Выбор источников
        st.subheader("📡 Источники данных:")
        all_sources = list(SOURCE_DISPLAY.keys())
        selected_sources = []
        for key in all_sources[:max_sources]:
            default = True
            selected = st.checkbox(SOURCE_DISPLAY[key], value=default, key=f"src_{key}")
            if selected:
                selected_sources.append(key)

        run_button = st.button("🚀 Запустить анализ", type="primary", use_container_width=True)

        # Экспорт
        if st.session_state.results_df is not None:
            st.divider()
            st.subheader("💾 Экспорт результатов")
            csv_path = "analysis_results.csv"
            xlsx_path = "analysis_results.xlsx"
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 CSV", use_container_width=True):
                    analyzer = PaperAnalyzer()
                    analyzer.export_csv(st.session_state.results_df, csv_path)
                    with open(csv_path, "rb") as f:
                        st.download_button(
                            "Скачать CSV",
                            f,
                            file_name=f"papers_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )
            with col2:
                if st.button("📥 Excel", use_container_width=True):
                    analyzer = PaperAnalyzer()
                    analyzer.export_excel(st.session_state.results_df, xlsx_path)
                    with open(xlsx_path, "rb") as f:
                        st.download_button(
                            "Скачать XLSX",
                            f,
                            file_name=f"papers_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )

    # --- MAIN CONTENT ---

    # Запуск анализа
    if run_button and query:
        st.session_state.query = query
        st.session_state.analysis_done = False

        with st.spinner("🔍 Сбор и анализ статей..."):
            analyzer = PaperAnalyzer()
            
            # Собираем статьи
            papers = analyzer.collect_papers(query, max_per_source=max_per_source)
            
            if not papers:
                st.error("❌ Не удалось найти статьи по вашему запросу. Попробуйте другие ключевые слова.")
                return

            # Анализируем
            df = analyzer.analyze_papers(papers)
            st.session_state.results_df = df
            st.session_state.analysis_done = True

        st.success(f"✅ Анализ завершён! Обработано {len(df)} статей.")
        
    elif run_button and not query:
        st.warning("⚠️ Пожалуйста, введите тему поиска.")

    # Отображение результатов
    if st.session_state.results_df is not None:
        df = st.session_state.results_df

        # --- СТАТИСТИКА ---
        st.header("📊 Сводка результатов")

        real_count = len(df[df["verdict"] == "Real ✅"])
        sus_count = len(df[df["verdict"] == "Suspicious ⚠️"])
        fake_count = len(df[df["verdict"] == "Fake ❌"])

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Всего статей", len(df))
        with col2:
            st.metric("✅ Достоверные", real_count)
        with col3:
            st.metric("⚠️ Подозрительные", sus_count)
        with col4:
            st.metric("❌ Фейковые", fake_count)

        # --- Цветовая индикация ---
        def color_verdict(value):
            if "Real" in str(value):
                return "background-color: #C6EFCE; color: #006100"
            elif "Suspicious" in str(value):
                return "background-color: #FFEB9C; color: #9C6500"
            elif "Fake" in str(value):
                return "background-color: #FFC7CE; color: #9C0006"
            return ""

        def color_score(value):
            if value >= 0.7:
                return "color: #006100"
            elif value >= 0.4:
                return "color: #9C6500"
            else:
                return "color: #9C0006"

        # --- ТАБЛИЦА РЕЗУЛЬТАТОВ ---
        st.header("📋 Результаты анализа")

        display_cols = [
            "title", "authors", "year", "source",
            "overall_score", "verdict"
        ]
        display_cols = [c for c in display_cols if c in df.columns]

        df_display = df[display_cols].copy()
        df_display.columns = [
            "Название", "Авторы", "Год", "Источник",
            "Score", "Вердикт"
        ]

        # Стилизация
        styled = df_display.style.applymap(color_verdict, subset=["Вердикт"])
        styled = styled.applymap(color_score, subset=["Score"])

        st.dataframe(
            styled,
            use_container_width=True,
            height=min(400, 50 * (len(df_display) + 1)),
            column_config={
                "Score": st.column_config.NumberColumn(format="%.2f"),
            }
        )

        # --- ДЕТАЛИ ПО КАЖДОЙ СТАТЬЕ ---
        st.header("🔍 Детальный разбор статей")

        # Нормализуем id для выбора
        df["_select_id"] = df.apply(
            lambda r: f"{r['title'][:80]}... | {r['source']} | Score: {r['overall_score']}",
            axis=1
        )

        selected_paper = st.selectbox(
            "Выберите статью для детального просмотра:",
            df["_select_id"].tolist(),
        )

        if selected_paper:
            paper_row = df[df["_select_id"] == selected_paper].iloc[0]

            tabs = st.tabs(["📄 Обзор", "📊 Анализ", "📝 Текст"])

            with tabs[0]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(paper_row["title"])
                    st.write(f"**Авторы:** {paper_row.get('authors', 'N/A')}")
                    st.write(f"**Год:** {paper_row.get('year', 'N/A')}")
                    st.write(f"**Источник:** {paper_row.get('source', 'N/A')}")
                    if paper_row.get("url"):
                        st.write(f"**URL:** [{paper_row['url']}]({paper_row['url']})")
                with col2:
                    verdict = paper_row["verdict"]
                    if "Real" in verdict:
                        st.success(f"### {verdict}")
                    elif "Suspicious" in verdict:
                        st.warning(f"### {verdict}")
                    else:
                        st.error(f"### {verdict}")
                    st.metric("Общий Score", f"{paper_row['overall_score']:.2f}")

            with tabs[1]:
                st.subheader("Оценка по критериям")

                # 3 колонки с метриками
                c1, c2, c3 = st.columns(3)
                with c1:
                    val = paper_row["citation_score"]
                    if val >= 0.7:
                        st.success(f"📊 Цитирования: {val:.2f}")
                    elif val >= 0.4:
                        st.warning(f"📊 Цитирования: {val:.2f}")
                    else:
                        st.error(f"📊 Цитирования: {val:.2f}")
                    st.caption(paper_row.get("citation_detail", ""))

                with c2:
                    val = paper_row["text_score"]
                    if val >= 0.7:
                        st.success(f"📝 Текст: {val:.2f}")
                    elif val >= 0.4:
                        st.warning(f"📝 Текст: {val:.2f}")
                    else:
                        st.error(f"📝 Текст: {val:.2f}")
                    st.caption(paper_row.get("text_detail", ""))

                with c3:
                    val = paper_row["journal_score"]
                    if val >= 0.7:
                        st.success(f"🏛️ Журнал: {val:.2f}")
                    elif val >= 0.4:
                        st.warning(f"🏛️ Журнал: {val:.2f}")
                    else:
                        st.error(f"🏛️ Журнал: {val:.2f}")
                    st.caption(paper_row.get("journal_detail", ""))

            with tabs[2]:
                st.subheader("Аннотация / Abstract")
                abstract = paper_row.get("abstract", "Нет данных")
                st.text_area("", value=abstract, height=200, disabled=True)

    # --- ПОДВАЛ ---
    st.divider()
    st.caption(
        "Science Paper Analyzer v1.0 | "
        "Источники: arXiv, Semantic Scholar, OpenReview, ACL Anthology, "
        "JMLR, ResearchGate (CrossRef), CyberLeninka, eLibrary (CrossRef), "
        "Dissercat (CrossRef), FIPS (CrossRef) | "
        "Beall's List встроен | "
        "Данные предоставляются 'как есть'"
    )


if __name__ == "__main__":
    main()