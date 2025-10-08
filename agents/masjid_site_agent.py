# agents/masjid_site_agent.py
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from core.schema import Masjid, Event


async def _render_html(url: str) -> str:
    """Use Playwright to render and return the full page HTML."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("networkidle")
        html = await page.content()
        await browser.close()
        return html


def _extract_events(html: str):
    """Very basic placeholder parser."""
    soup = BeautifulSoup(html, "html.parser")
    events = []
    for e in soup.select(".event, [class*='event']"):
        title = e.get_text(strip=True)[:150]
        if title:
            events.append(Event(title=title))
    return events


async def scrape_masjid(url: str) -> dict:
    """Scrape a masjid website and return a normalized dict."""
    html = await _render_html(url)
    events = _extract_events(html)
    name = url.split("//")[-1].split("/")[0]
    masjid = Masjid(name=name, source=url, events=events)
    return masjid.dict()


if __name__ == "__main__":
    test_url = "https://example.com"
    result = asyncio.run(scrape_masjid(test_url))
    print(result)