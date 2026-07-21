#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор налогов и оборота компаний.
Источники: Контур.Фокус API, Checko, ЗаЧестныйБизнес.
"""

import json
import logging
import os
from typing import Dict, Optional

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaxAnalyzer:
    """Анализ финансовых показателей компании по ИНН/БИН."""

    def __init__(self):
        self.kontur_api_key = os.getenv("KONTUR_API_KEY", "")
        self.checko_api_key = os.getenv("CHECKO_API_KEY", "")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "application/json",
        })

    def get_kontur_data(self, inn: str) -> Optional[Dict]:
        """Получить данные из Контур.Фокус API."""
        if not self.kontur_api_key:
            logger.warning("KONTUR_API_KEY не задан")
            return None

        url = "https://focus-api.kontur.ru/api3/req"
        params = {"inn": inn, "key": self.kontur_api_key}

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                data = data[0]

            return self._parse_kontur(data)
        except Exception as e:
            logger.error("Ошибка Контур.Фокус для %s: %s", inn, e)
            return None

    def _parse_kontur(self, data: Dict) -> Dict:
        """Извлечь ключевые метрики из ответа Контур."""
        analytics = data.get("analytics", {}) or {}
        contacts = data.get("contacts", {}) or {}
        ceo = data.get("ceo", {}) or {}

        return {
            "source": "kontur",
            "inn": data.get("inn", ""),
            "name": data.get("name", ""),
            "ogrn": data.get("ogrn", ""),
            "okved": data.get("okved", ""),
            "status": data.get("status", ""),
            "turnover": analytics.get("turnover", 0),
            "taxes_year": analytics.get("taxes", {}).get("year", 0),
            "taxes_quarter": analytics.get("taxes", {}).get("quarter", 0),
            "employees": analytics.get("employees", 0),
            "capital": data.get("capital", 0),
            "ceo_name": ceo.get("name", ""),
            "ceo_position": ceo.get("position", ""),
            "phone": contacts.get("phone", ""),
            "email": contacts.get("email", ""),
            "website": contacts.get("website", ""),
            "address": data.get("address", ""),
            "region": data.get("region", ""),
        }

    def get_checko_data(self, inn: str) -> Optional[Dict]:
        """Получить данные из Checko API."""
        if not self.checko_api_key:
            return None

        url = f"https://api.checko.com/v1/company/{inn}"
        headers = {"Authorization": f"Bearer {self.checko_api_key}"}

        try:
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return self._parse_checko(response.json())
        except Exception as e:
            logger.error("Ошибка Checko для %s: %s", inn, e)
            return None

    def _parse_checko(self, data: Dict) -> Dict:
        """Извлечь метрики из Checko."""
        finance = data.get("finance", {}) or {}
        ceo = data.get("ceo", {}) or {}

        return {
            "source": "checko",
            "inn": data.get("inn", ""),
            "name": data.get("name", ""),
            "turnover": finance.get("revenue", 0),
            "taxes_year": finance.get("taxes", 0),
            "employees": data.get("employees", 0),
            "ceo_name": ceo.get("name", ""),
            "ceo_position": ceo.get("position", ""),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "website": data.get("website", ""),
        }

    def analyze(self, inn: str) -> Dict:
        """Собрать налоговые данные из всех доступных источников."""
        result = {
            "inn": inn,
            "sources_checked": [],
            "sources_failed": [],
            "data": {},
        }

        kontur = self.get_kontur_data(inn)
        if kontur:
            result["sources_checked"].append("kontur")
            result["data"] = kontur
        else:
            result["sources_failed"].append("kontur")

        checko = self.get_checko_data(inn)
        if checko:
            result["sources_checked"].append("checko")
            if not result["data"]:
                result["data"] = checko
            else:
                for key, value in checko.items():
                    if value and not result["data"].get(key):
                        result["data"][key] = value
        else:
            result["sources_failed"].append("checko")

        return result

    @staticmethod
    def format_for_report(data: Dict) -> str:
        """Красивый текст для вставки в отчёт."""
        d = data.get("data", {})
        if not d:
            return "❌ Налоговые данные не найдены"

        lines = [
            f"### Финансовый анализ",
            f"",
            f"- **Компания:** {d.get('name', '—')}",
            f"- **ИНН:** {d.get('inn', '—')}",
            f"- **Статус:** {d.get('status', '—')}",
            f"",
            f"**💰 Оборот за год:** {TaxAnalyzer._fmt_money(d.get('turnover', 0))}",
            f"**📊 Налоги за год:** {TaxAnalyzer._fmt_money(d.get('taxes_year', 0))}",
            f"**📈 Налоги за квартал:** {TaxAnalyzer._fmt_money(d.get('taxes_quarter', 0))}",
            f"**👥 Сотрудники:** {d.get('employees', '—')}",
            f"**💵 Уставный капитал:** {TaxAnalyzer._fmt_money(d.get('capital', 0))}",
            f"",
            f"**👤 Руководитель:** {d.get('ceo_name', '—')} ({d.get('ceo_position', '—')})",
            f"**📞 Телефон:** {d.get('phone', '—')}",
            f"**📧 Email:** {d.get('email', '—')}",
            f"**🌐 Сайт:** {d.get('website', '—')}",
            f"**📍 Адрес:** {d.get('address', '—')}",
            f"",
            f"*Источники: {', '.join(data.get('sources_checked', []))}*",
        ]
        return "\n".join(lines)

    @staticmethod
    def _fmt_money(value) -> str:
        """Форматировать число как деньги."""
        try:
            if value >= 1_000_000_000:
                return f"{value / 1_000_000_000:.1f} млрд ₽"
            elif value >= 1_000_000:
                return f"{value / 1_000_000:.1f} млн ₽"
            elif value >= 1_000:
                return f"{value / 1_000:.0f} тыс ₽"
            else:
                return f"{value} ₽"
        except (TypeError, ValueError):
            return str(value)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python tax_analyzer.py <ИНН>")
        sys.exit(1)

    inn = sys.argv[1]
    analyzer = TaxAnalyzer()
    result = analyzer.analyze(inn)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n" + "=" * 50)
    print(analyzer.format_for_report(result))