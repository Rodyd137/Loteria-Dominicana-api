# API estática de resultados de Loterías (RD)

Este repo raspa **https://loteriasdominicanas.com/** y publica `public/data.json` con los últimos resultados visibles en la home.

## Cómo usar

1. Sube este repo a GitHub.
2. (Opcional) En *Settings → Secrets and variables → Actions*, crea `SOURCE_URL` con `https://loteriasdominicanas.com/`.
3. En *Actions*, ejecuta el workflow **Scrape & Publish** (o espera el cron cada 15 min).
4. Consume el JSON desde:
   - **Raw:** `https://raw.githubusercontent.com/<usuario>/<repo>/main/public/data.json`
   - **Pages:** `https://<usuario>.github.io/<repo>/data.json` (si activas Pages)
   - **jsDelivr:** `https://cdn.jsdelivr.net/gh/<usuario>/<repo>@main/public/data.json`

## Formato del JSON

```json
{
  "source": "https://loteriasdominicanas.com/",
  "scraped_at": "2025-08-19T23:59:00Z",
  "page_date": "2025-08-19",
  "count": 0,
  "results": [
    {
      "company": "Nacional",
      "company_url": "/loteria-nacional",
      "game": "Gana Más",
      "game_url": "/loteria-nacional/gana-mas",
      "logo": "https://...png",
      "session_date": "2025-08-19",
      "scores": [{"value": "68", "tag": null}, {"value": "33", "tag": null}, {"value": "04", "tag": null}],
      "is_past": false,
      "theme": "company-block-10"
    }
  ]
}
```

- `scores.tag` puede ser `null`, `bonus`, `special1`, `special2` o `special3` (útil para pintar bolas especiales).
- `theme` refleja clases como `company-block-10` por si quieres mapear colores en el front.

## Nota legal
Scraping de contenido público. Respeta Términos/robots y usa una frecuencia razonable.
