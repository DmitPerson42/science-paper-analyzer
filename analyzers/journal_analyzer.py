"""
Journal Analyzer — проверка журнала по Beall's List
Встроенный список хищнических журналов и известных доверенных журналов
"""

from typing import Tuple


# Список известных хищнических журналов (Beall's List — топ-200+)
PREDATORY_JOURNALS = [
    "american journal of engineering research",
    "international journal of engineering research and technology",
    "international journal of computer applications",
    "international journal of scientific and technology research",
    "journal of engineering and technology research",
    "journal of applied sciences research",
    "journal of engineering and applied sciences",
    "research journal of applied sciences",
    "world journal of engineering and technology",
    "international research journal of engineering and technology",
    "international journal of advanced research in computer science",
    "international journal of computer science and information technologies",
    "international journal of engineering sciences and research technology",
    "international journal of innovative research in science",
    "international journal of current research",
    "international journal of science and research",
    "international journal of research in engineering and technology",
    "international journal of engineering research and general science",
    "international journal of engineering science and technology",
    "international journal of recent technology and engineering",
    "international journal of innovative technology and exploring engineering",
    "international journal of engineering and advanced technology",
    "international journal of management and technology",
    "international journal of applied engineering research",
    "international journal of engineering and technology",
    "journal of engineering and technology",
    "international journal of research in engineering and science",
    "global journal of engineering and technology",
    "international journal of innovative research in science and engineering",
    "international journal of advanced engineering research and science",
    "journal of chemical and pharmaceutical research",
    "international journal of pharmacy and pharmaceutical sciences",
    "international journal of pharmaceutical sciences and research",
    "journal of pharmacy and pharmaceutical sciences",
    "international journal of pharmaceutical sciences review and research",
    "journal of pharmaceutical research",
    "international journal of pharmaceutical research",
    "journal of pharmaceutical science and technology",
    "journal of pharmacy research",
    "journal of applied pharmaceutical science",
    "journal of biology and today's world",
    "journal of biological sciences",
    "journal of life sciences",
    "international journal of biological sciences",
    "research journal of biological sciences",
    "journal of plant sciences",
    "journal of animal science",
    "international journal of current microbiology and applied sciences",
    "journal of environmental science and engineering",
    "international journal of environmental science and development",
    "journal of environmental science",
    "international journal of environmental science",
    "indian journal of science and technology",
    "pakistan journal of scientific and industrial research",
    "journal of research in engineering and applied sciences",
    "journal of international academic research for multidisciplinary",
    "international journal of multidisciplinary research",
    "international journal of research",
    "international journal of scientific research",
    "international journal of academic research",
    "journal of multidisciplinary research",
    "international journal of multidisciplinary sciences and engineering",
    "international research journal of engineering and technology (irjet)",
    "journal of emerging technologies and innovative research",
    "international journal of pure and applied mathematics",
    "far east journal of mathematical sciences",
    "journal of mathematics and statistics",
    "journal of engineering and scientific research",
    "journal of advanced research in dynamical and control systems",
    "journal of critical reviews",
    "journal of computational and theoretical nanoscience",
    "journal of applied mathematics and physics",
    "journal of modern physics",
    "journal of applied science and engineering",
    "international journal of applied physics and mathematics",
    "science and engineering research support society",
    "scientific research publishing (scirp)",
    "academic journals",
    "academic research journals",
    "academic publishing",
    "advance journals",
    "aizeon publishers",
    "australian research journals",
    "avid science",
    "bentham open",
    "canadian center of science and education",
    "clausius scientific press",
    "crimson publishers",
    "david publishing",
    "e-palli publishers",
    "european journal of academic research",
    "global journals",
    "iaeme publication",
    "imedpub",
    "international journal of sciences",
    "international journal of contemporary",
    "international technology and science",
    "internet scientific publications",
    "iospress",
    "iris publishers",
    "juniper publishers",
    "krishtol journals",
    "longbridge publishing",
    "macrothink institute",
    "marshall journal",
    "mecs publisher",
    "medwell publishing",
    "oapublishing",
    "ojs",
    "omed",
    "one central press",
    "open access journals",
    "open access pub",
    "open science",
    "pacific group of e-journals",
    "pencraft journals",
    "primrose journals",
    "publishing house",
    "pulsus group",
    "research publish journals",
    "research publishing",
    "researchpub",
    "remedy publications",
    "royal publications",
    "science academy publisher",
    "science alert",
    "science domain international",
    "science publishing corporation",
    "science publications",
    "science publishing group",
    "scientific & academic publishing",
    "scientific advances",
    "scientific research journals",
    "scitech research journals",
    "scitec publications",
    "serial journals",
    "serial publishers",
    "sigma journals",
    "sm journals",
    "sryahwa publications",
    "scientific journals international",
    "scholarly journals",
    "scholars journal",
    "stanford journals",
    "swan journals",
    "the international journal of science and technology",
    "the international journal of engineering and science",
    "the research publication",
    "trade science inc.",
    "transstellar journal",
    "universal research journals",
    "valley international",
    "vernon press",
    "waset (world academy of science, engineering and technology)",
    "world research journals",
    "world science publisher",
    "wudpecker research journals",
    "zed science press",
    "zenith journals",
    "journal of economics and sustainable development",
    "journal of finance and economics",
    "journal of business and economic development",
    "journal of management and sustainability",
    "international journal of business and management",
    "international journal of economics and finance",
    "international journal of marketing studies",
    "journal of educational and social research",
    "journal of education and practice",
    "journal of language teaching and research",
    "english language teaching",
    "theory and practice in language studies",
    "studies in literature and language",
    "international journal of applied linguistics",
    "journal of law and conflict resolution",
    "journal of law, policy and globalization",
    "scientific papers of the university of par dubice",
    "procedia - social and behavioral sciences (elsevier — real, but some series)",
]

# Список известных доверенных журналов/площадок
TRUSTED_VENUES = [
    "nature", "science", "cell", "pnas", "nejm", "lancet", "jama",
    "ieee", "acl", "emnlp", "neurips", "icml", "cvpr", "iccv",
    "arxiv", "jmlr", "springer", "elsevier", "acm", "mit press",
    "oxford university press", "cambridge university press",
    "sage", "taylor and francis", "wiley", "frontiers",
    "plos", "mdpi", "ieee transactions", "journal of machine learning research",
    "acl anthology", "acl proceedings",
    "transactions of the association for computational linguistics",
    "computational linguistics", "journal of artificial intelligence research",
    "artificial intelligence", "machine learning",
    "neural information processing systems",
    "international conference on machine learning",
    "computational linguistics association",
    "american physical society", "royal society of chemistry",
    "american chemical society", "iop publishing",
    "annual reviews", "bmc", "nature research",
    "science advances", "nature communications",
    "proceedings of the national academy of sciences",
    "physical review", "applied physics letters",
    "journal of applied physics", "journal of chemical physics",
    "openreview", "semantic scholar",
]


class JournalAnalyzer:
    def __init__(self):
        self.predatory_set = set(PREDATORY_JOURNALS)
        self.trusted_set = set(v.lower() for v in TRUSTED_VENUES)

    def analyze(self, paper: dict) -> Tuple[float, str]:
        """
        Оценка журнала/площадки публикации.
        Возвращает (score, detail):
            score 0.0–1.0 (выше = более реальный)
        """
        venue = paper.get("venue", paper.get("journal", ""))
        source = paper.get("source", "")
        source_display = paper.get("source_display", "")
        publisher = paper.get("publisher", "")
        source_context = paper.get("source_context", "")

        # Объединяем все возможные источники названия площадки
        venue_text = " ".join([
            str(venue or ""),
            str(source or ""),
            str(source_display or ""),
            str(publisher or ""),
            str(source_context or ""),
        ]).lower().strip()

        if not venue_text:
            return 0.5, "Нет данных о журнале/площадке — оценка нейтральная"

        # Проверка на доверенные площадки
        for trusted in self.trusted_set:
            if trusted in venue_text and len(trusted) > 3:
                return 0.95, f"Площадка '{venue}' признана доверенной"

        # Проверка на хищнические журналы
        for predatory in self.predatory_set:
            if predatory in venue_text and len(predatory) > 5:
                return 0.15, f"Журнал/площадка '{venue}' найдена в Beall's List (хищнический журнал)"

        # Если конкретная площадка не найдена в списках
        return 0.6, f"Журнал/площадка '{venue}' не найдена в Beall's List — нейтральная оценка"