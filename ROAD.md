## 7. Инструкция по загрузке на GitHub

### 7.1 Создание репозитория на GitHub

1. Перейдите на https://github.com/new
2. В поле **Repository name** введите: `science-paper-analyzer`
3. Оставьте **Public** (или выберите Private, если нужно)
4. **НЕ** создавайте README, .gitignore или лицензию (они уже есть в проекте)
5. Нажмите **Create repository**

### 7.2 Загрузка кода (через терминал/PowerShell)

```bash
# Замените PATH на путь к проекту
cd D:\work2

# Инициализация Git
git init
git add .
git commit -m "Initial commit: Science Paper Analyzer v1.0"

# Привязка к удалённому репозиторию
git remote add origin https://github.com/DmitPerson42/science-paper-analyzer.git

# Отправка кода
git push -u origin main
```

### 7.3 Если нужно авторизоваться

GitHub больше не принимает пароли. Используйте **Personal Access Token (PAT)**:

1. Перейдите: https://github.com/settings/tokens
2. Нажмите **Generate new token (classic)**
3. Выберите scope: `repo` (полный доступ)
4. Скопируйте токен
5. При push введите:
   - Username: `DmitPerson42`
   - Password: (вставьте токен)

### 7.4 Альтернатива — GitHub Desktop

1. Скачайте: https://desktop.github.com/
2. File → Add local repository → выберите `D:\work2`
3. Commit и Publish

### 7.5 Google Colab

После загрузки на GitHub:
1. Откройте: https://colab.research.google.com/
2. File → Open notebook → GitHub
3. Вставьте: `https://github.com/DmitPerson42/science-paper-analyzer`
4. Выберите `science_paper_analyzer.ipynb`

Или прямая ссылка:
```
https://colab.research.google.com/github/DmitPerson42/science-paper-analyzer/blob/main/science_paper_analyzer.ipynb
```

### 7.6 Файлы для загрузки

Все необходимые файлы находятся в `D:\work2\`:

```
📦 science-paper-analyzer/
├── 📄 app.py                    # Веб-приложение Streamlit
├── 📄 analyzer.py               # Центральный координатор
├── 📄 requirements.txt          # Зависимости
├── 📄 ROAD.md                   # Полная документация разработки
├── 📄 README.md                 # Инструкция по запуску
├── 📄 science_paper_analyzer.ipynb  # Google Colab ноутбук
├── 📄 .gitignore                # Исключения Git
├── 📁 parsers/                  # Парсеры для 10 сайтов
│   ├── arxiv_parser.py
│   ├── semantic_scholar.py
│   ├── openreview_parser.py
│   ├── aclanthology.py
│   ├── jmlr_parser.py
│   ├── crossref_fallback.py
│   └── cyberleninka.py
├── 📁 analyzers/                # Анализаторы
│   ├── citation_analyzer.py
│   ├── text_analyzer.py
│   └── journal_analyzer.py
└── 📁 exporters/                # Экспортёры
    ├── csv_exporter.py
    └── excel_exporter.py
```