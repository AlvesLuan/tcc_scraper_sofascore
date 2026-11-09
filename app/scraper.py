import time
from patchright.sync_api import sync_playwright, Page
from config import REQUEST_DELAY, UNIQUE_TOURNAMENT_ID

_playwright = None
_browser = None
_page = None

JS_FETCH = """
async (url) => {
    const r = await fetch(url, {credentials: 'include'});
    if (!r.ok) return {__status: r.status};
    return await r.json();
}
"""

def get_page() -> Page:
    global _playwright, _browser, _page
    if _page is None:
        _playwright = sync_playwright().start()
        #_browser = _playwright.chromium.launch(headless=True)
        _browser = _playwright.chromium.launch(headless=True)
        _page = _browser.new_page()
        _page.goto("https://www.sofascore.com", wait_until="domcontentloaded")
        time.sleep(2)
    return _page

def buscar(url: str, tentativas: int = 4) -> dict:
    page = get_page()
    for i in range(tentativas):
        time.sleep(REQUEST_DELAY)
        data = page.evaluate(JS_FETCH, url)
        status = data.get("__status") if isinstance(data, dict) else None
        if status is None:
            return data
        print(f"    [scraper] HTTP {status} em {url} (tentativa {i+1})")
        time.sleep(5 * (i + 1))  # backoff
    raise RuntimeError(f"Falha ao buscar {url}")

def close():
    global _playwright, _browser, _page
    if _browser:
        _browser.close()
    if _playwright:
        _playwright.stop()
    _browser = _playwright = _page = None

def get_classificacao(season_id: int) -> dict:
    url = f"https://www.sofascore.com/api/v1/unique-tournament/{UNIQUE_TOURNAMENT_ID}/season/{season_id}/standings/total"
    print(f"    [scraper] Classificação season_id={season_id}")
    return buscar(url)

def get_jogos_time(team_id: int, page: int = 0) -> dict:
    return buscar(f"https://www.sofascore.com/api/v1/team/{team_id}/events/last/{page}")