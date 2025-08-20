import os, re, json, time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Puedes cambiar esta URL aquí o via variable de entorno SOURCE_URL en el workflow
SOURCE_URL = os.getenv("SOURCE_URL", "https://loteriasdominicanas.com/")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

def parse_datepicker(html: str):
    """
    Busca en el HTML el init del datepicker, por ejemplo:
    date: '19-08-2025'
    """
    m = re.search(r"date:\s*'(\d{2}-\d{2}-\d{4})'", html)
    if m:
        try:
            return datetime.strptime(m.group(1), "%d-%m-%Y").date().isoformat()
        except ValueError:
            pass
    # Fallback: hoy UTC
    return datetime.utcnow().date().isoformat()

def clean_text(x):
    return re.sub(r"\s+", " ", x).strip() if x else None

def get_attr(el, *attrs):
    for a in attrs:
        if not el:
            return None
        if el.has_attr(a):
            return el.get(a)
    return None

def scrape():
    r = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    html = r.text
    soup = BeautifulSoup(html, "lxml")

    page_date = parse_datepicker(html)  # ISO date (YYYY-MM-DD)

    results = []
    for block in soup.select(".game-block"):
        # compañía / lotería (en .company-title a > text)
        company_title = block.select_one(".company-title a")
        company = clean_text(company_title.get_text()) if company_title else None
        company_href = get_attr(company_title, "href")

        # juego (en .game-title a > span)
        game_title_link = block.select_one(".game-title")
        game_title = clean_text(game_title_link.get_text()) if game_title_link else None
        game_href = get_attr(game_title_link, "href")

        # fecha visible (dd-mm) + convertir usando year del datepicker
        session_date_el = block.select_one(".session-date")
        session_dm = clean_text(session_date_el.get_text()) if session_date_el else None
        session_date_iso = None
        if session_dm and re.match(r"\d{2}-\d{2}", session_dm):
            try:
                year = int(page_date.split("-")[0])
                d, m = map(int, session_dm.split("-"))
                session_date_iso = datetime(year, m, d).date().isoformat()
            except Exception:
                session_date_iso = page_date
        else:
            session_date_iso = page_date

        # logo (data-src o src)
        logo_el = block.select_one(".game-logo img")
        logo = get_attr(logo_el, "data-src", "src")

        # scores con etiquetas
        scores = []
        for s in block.select(".game-scores .score"):
            val = clean_text(s.get_text())
            classes = s.get("class", [])
            tag = None
            for t in ["bonus", "special1", "special2", "special3"]:
                if t in classes:
                    tag = t
                    break
            scores.append({"value": val, "tag": tag})

        # estado (si tiene clase 'past')
        is_past = "past" in (block.get("class") or [])

        # company-block-XX (paleta/tema)
        theme_class = None
        for c in (block.get("class") or []):
            if c.startswith("company-block-"):
                theme_class = c
                break

        if game_title and scores:
            results.append({
                "company": company,
                "company_url": company_href,
                "game": game_title,
                "game_url": game_href,
                "logo": logo,
                "session_date": session_date_iso,
                "scores": scores,
                "is_past": is_past,
                "theme": theme_class
            })

    payload = {
        "source": SOURCE_URL,
        "scraped_at_unix": int(time.time()),
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "page_date": page_date,
        "count": len(results),
        "results": results
    }
    return payload

def main():
    data = scrape()
    os.makedirs("public", exist_ok=True)
    with open("public/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"OK: {data['count']} juegos guardados en public/data.json")

if __name__ == "__main__":
    main()
