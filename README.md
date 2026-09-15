# 🔬 Science Paper Analyzer

Система для парсинга и верификации научных статей из 10+ источников с определением фейковых/недостоверных публикаций.

**Тема диссертации:** Разработка методов фильтрации генеративных текстовых данных для предотвращения коллапса языковых моделей

---

## 🚀 Быстрый старт

### Вариант 1 — Google Colab (рекомендуется)
1. Откройте [`science_paper_analyzer.ipynb`](science_paper_analyzer.ipynb) в Google Colab
2. Запустите ячейки по порядку
3. Введите тему поиска и получите результаты

### Вариант 2 — Локальный запуск
```bash
# 1. Клонируйте репозиторий
git clone https://github.com/ВАШ_АККАУНТ/science-paper-analyzer.git
cd science-paper-analyzer

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Запустите веб-интерфейс
streamlit run app.py
```

### Вариант 3 — Python скрипт
```python
from analyzer import PaperAnalyzer

analyzer = PaperAnalyzer()
papers = analyzer.collect_papers("your research topic")
df = analyzer.analyze_papers(papers)
analyzer.export_csv(df, "results.csv")
analyzer.export_excel(df, "results.xlsx")
```

---

## 📡 Источники данных

| Источник | Метод | Статус |
|----------|-------|--------|
| [arXiv.org](https://arxiv.org) | REST API | ✅ |
| [Semantic Scholar](https://semanticscholar.org) | REST API | ✅ |
| [OpenReview.net](https://openreview.net) | REST API | ✅ |
| [ACL Anthology](https://aclanthology.org) | REST API | ✅ |
| [JMLR.org](https://jmlr.org) | Scraping | ✅ |
| [ResearchGate](https://researchgate.net) | CrossRef API | ✅ |
| [CyberLeninka.ru](https://cyberleninka.ru) | Scraping | ✅ |
| [eLibrary.ru](https://elibrary.ru) | CrossRef API | ✅ |
| [Dissercat.com](https://dissercat.com) | CrossRef API | ✅ |
| [FIPS.ru](https://fips.ru) | CrossRef API | ✅ |

---

## 🔍 Критерии оценки

Статья получает **Score** от 0.0 (фейк) до 1.0 (достоверная) по трём параметрам:

### 1. 📊 Цитируемость (Citation Score)
- **0 цит.** + возраст ≥3 лет → низкое доверие (0.2)
- **0 цит.** + молодая статья → нейтрально (0.5)
- **1–5 цит.** → нормально (0.7)
- **5–15 цит.** → хорошо (0.85)
- **>15 цит.** → высокое доверие (0.95)

### 2. 📝 Текст (Text Score)
Эвристический анализ на признаки AI-генерации:
- Поиск AI-маркерных фраз
- Лексическое разнообразие (TTR)
- Повторяющиеся n-граммы
- Равномерность длины предложений
- Доля стоп-слов

### 3. 🏛️ Журнал (Journal Score)
- Проверка по **Beall's List** (>200 хищнических журналов)
- Проверка по списку доверенных площадок (Nature, Science, IEEE, ACL, arXiv и др.)
- Если не найден в списках → нейтральная оценка

### Итоговый вердикт
| Score | Вердикт |
|-------|---------|
| ≥0.7 | ✅ **Real** |
| 0.4–0.7 | ⚠️ **Suspicious** |
| <0.4 | ❌ **Fake** |

---

## 📁 Структура проекта

```
science-paper-analyzer/
├── app.py                    # Streamlit веб-приложение
├── analyzer.py               # Центральный координатор
├── requirements.txt          # Зависимости
├── ROAD.md                   # Полная документация разработки
├── README.md                 # Эта инструкция
├── science_paper_analyzer.ipynb  # Google Colab ноутбук
├── parsers/
│   ├── arxiv_parser.py       # Парсер arXiv
│   ├── semantic_scholar.py   # Парсер Semantic Scholar
│   ├── openreview_parser.py  # Парсер OpenReview
│   ├── aclanthology.py       # Парсер ACL Anthology
│   ├── jmlr_parser.py        # Парсер JMLR
│   ├── crossref_fallback.py  # Универсальный парсер (CrossRef)
│   └── cyberleninka.py       # Парсер CyberLeninka
├── analyzers/
│   ├── citation_analyzer.py  # Анализ цитируемости
│   ├── text_analyzer.py      # Анализ текста (AI-детектор)
│   └── journal_analyzer.py   # Анализ журнала (Beall's List)
├── exporters/
│   ├── csv_exporter.py       # Экспорт в CSV
│   └── excel_exporter.py     # Экспорт в Excel
└── data/                     # Директория для результатов
```

---

## 💻 Веб-интерфейс

После запуска `streamlit run app.py` откройте `http://localhost:8501`.

**Функции:**
- Ввод темы поиска
- Выбор источников
- Цветовая индикация результатов
- Детальный разбор каждой статьи
- Экспорт в CSV/Excel

---

## 📦 Зависимости

```
streamlit>=1.28.0
requests>=2.28.0
pandas>=1.5.0
openpyxl>=3.0.0
lxml>=4.9.0
beautifulsoup4>=4.11.0
numpy>=1.23.0
scikit-learn>=1.2.0
plotly>=5.14.0
```

---

## 🔗 GitHub

Репозиторий: [https://github.com/ВАШ_АККАУНТ/science-paper-analyzer](https://github.com/ВАШ_АККАУНТ/science-paper-analyzer)

---

## 📄 Лицензия

MIT. Данные предоставляются "как есть". Beall's List встроен в код программы.