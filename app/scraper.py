import time
from playwright.sync_api import (
    sync_playwright,
    Page
)
from config import (REQUEST_DELAY, UNIQUE_TOURNAMENT_ID)


_playwright = None
_browser = None
_page = None

def get_page() -> Page:
    global _playwright, _browser, _page
    if _page is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=True)
        _page = _browser.new_page()
        # Abre o Sofascore uma vez para pegar cookies de sessão
        _page.goto("https://www.sofascore.com", wait_until="domcontentloaded")
        time.sleep(2)
    return _page

def fetch(url: str) -> dict:
    time.sleep(REQUEST_DELAY)
    page = get_page()
    response = page.goto(url, wait_until="domcontentloaded")
    return response.json()

def close():
    global _playwright, _browser, _page
    if _browser:
        _browser.close()
    if _playwright:
        _playwright.stop()
    _browser = None
    _page = None
    _playwright = None

def fetch_standings(season_id: int) -> dict:
    url = f"https://www.sofascore.com/api/v1/unique-tournament/{UNIQUE_TOURNAMENT_ID}/season/{season_id}/standings/total"
    print(f"  [scraper] Classificação season_id={season_id}")
    return fetch(url)

def fetch_team_events(team_id: int, page: int = 0) -> dict:
    url = f"https://www.sofascore.com/api/v1/team/{team_id}/events/last/{page}"
    return fetch(url)