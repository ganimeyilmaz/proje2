from app.crawler.adapters.base import UniversityCatalogAdapter
from app.crawler.adapters.bologna import BolognaLikeAdapter
from app.crawler.adapters.generic_html import GenericHtmlTableAdapter


ADAPTERS: list[UniversityCatalogAdapter] = [
    BolognaLikeAdapter(),
    GenericHtmlTableAdapter(),
]


def select_adapter(html: str, url: str, preferred: str | None = None) -> UniversityCatalogAdapter:
    if preferred:
        for adapter in ADAPTERS:
            if adapter.name == preferred:
                return adapter
    for adapter in ADAPTERS:
        if adapter.can_parse(html, url):
            return adapter
    return GenericHtmlTableAdapter()
