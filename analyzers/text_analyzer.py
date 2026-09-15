"""
Text Analyzer — ML-детектор сгенерированного текста
Анализирует текст статьи на признаки AI-генерации
"""

from typing import Tuple
import re
import math


class TextAnalyzer:
    def __init__(self):
        # Фразы-маркеры AI-сгенерированного текста
        self.ai_markers = [
            "as an ai", "as a language model", "as an artificial intelligence",
            "i cannot", "i'm sorry", "i apologize", "i don't have",
            "it is important to note", "in conclusion", "additionally",
            "furthermore", "moreover", "in recent years",
            "there has been growing interest", "in this paper we propose",
            "state-of-the-art", "cutting-edge", "revolutionary",
            "groundbreaking", "leveraging", "harnessing the power",
        ]

        # Чрезмерно повторяющиеся структуры
        self.low_complexity_patterns = [
            r'\b(this|that|these|those) (is|are) (a|an|the)',
            r'\bin (order|other|this|terms|conclusion)\b',
            r'\bas well as\b',
            r'\bdue to the fact that\b',
            r'\bin the context of\b',
        ]

    def analyze(self, paper: dict) -> Tuple[float, str]:
        """
        Оценка текста на признаки AI-генерации.
        Возвращает (score, detail):
            score 0.0–1.0 (выше = более реальный/человеческий)
        """
        text = ""
        # Собираем весь доступный текст
        for field in ["title", "abstract", "summary"]:
            val = paper.get(field, "")
            if val:
                text += " " + str(val)

        text = text.strip()
        if not text or len(text) < 50:
            return 0.5, "Недостаточно текста для анализа"

        text_lower = text.lower()
        words = text.split()
        n_words = len(words)
        if n_words == 0:
            return 0.5, "Пустой текст"

        # --- 1. Доля AI-маркеров ---
        marker_hits = sum(1 for m in self.ai_markers if m in text_lower)
        marker_density = marker_hits / max(len(self.ai_markers), 1)
        marker_score = 1.0 - min(marker_density * 3, 0.8)

        # --- 2. Лексическое разнообразие (TTR — Type-Token Ratio) ---
        unique_words = set(w.lower() for w in words)
        ttr = len(unique_words) / n_words
        # Нормальный TTR для научного текста: 0.5–0.8
        ttr_score = 1.0 - abs(ttr - 0.65) / 0.65  # 1.0 при TTR=0.65

        # --- 3. Повторяющиеся n-граммы ---
        repeat_penalty = 0.0
        if n_words > 10:
            seen_ngrams = set()
            total_ngrams = 0
            for i in range(n_words - 2):
                ngram = " ".join(words[i:i+3]).lower()
                if ngram in seen_ngrams:
                    repeat_penalty += 0.02
                seen_ngrams.add(ngram)
                total_ngrams += 1
            repeat_penalty = min(repeat_penalty, 0.5)

        # --- 4. Средняя длина предложений (слишком равномерная = AI) ---
        sentences = re.split(r'[.!?]+', text)
        sent_lengths = [len(s.split()) for s in sentences if len(s.split()) > 2]
        if sent_lengths:
            avg_len = sum(sent_lengths) / len(sent_lengths)
            std_len = (sum((l - avg_len) ** 2 for l in sent_lengths) / len(sent_lengths)) ** 0.5
            rel_std = std_len / max(avg_len, 1)
            # Нормальный текст: std/avg ~0.5-0.9
            if rel_std < 0.3:
                uniformity_penalty = 0.2  # слишком равномерно → AI
            elif rel_std > 1.2:
                uniformity_penalty = 0.1  # слишком разнообразно → тоже подозрительно
            else:
                uniformity_penalty = 0.0
        else:
            uniformity_penalty = 0.0

        # --- 5. Частота стоп-слов ---
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                      "of", "with", "by", "as", "is", "are", "was", "were", "be", "been",
                      "being", "have", "has", "had", "do", "does", "did", "will", "would",
                      "can", "could", "may", "might", "shall", "should", "this", "that"}
        stop_count = sum(1 for w in words if w.lower() in stop_words)
        stop_ratio = stop_count / n_words
        # Научные тексты ~40-55% стоп-слов; выше 60% — подозрительно
        if stop_ratio > 0.60:
            stop_penalty = min((stop_ratio - 0.60) * 2, 0.3)
        else:
            stop_penalty = 0.0

        # Итоговый score
        score = marker_score * 0.3 + ttr_score * 0.2 + (1.0 - repeat_penalty) * 0.25 + (1.0 - uniformity_penalty) * 0.1 + (1.0 - stop_penalty) * 0.15
        score = max(0.0, min(1.0, score))

        # Детали
        issues = []
        if marker_hits > 3:
            issues.append(f"{marker_hits} AI-маркеров найдено")
        if ttr < 0.4:
            issues.append(f"низкое лексическое разнообразие (TTR={ttr:.2f})")
        if repeat_penalty > 0.2:
            issues.append("много повторяющихся фраз")
        if stop_penalty > 0.1:
            issues.append("высокая доля стоп-слов")

        if not issues:
            detail = "Текст выглядит естественным, признаков AI-генерации не обнаружено"
        else:
            detail = f"Обнаружены признаки: {'; '.join(issues)}"

        return score, detail