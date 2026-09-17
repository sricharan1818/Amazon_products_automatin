# Amazon Product Scraper (Playwright + Python)

A browser-automation script that searches Amazon India for "laptop", scrapes the top 10 results (name, price, URL, description), and saves the data as structured JSON.

## What it does

1. Opens Amazon.in in a real Chrome browser (via Playwright)
2. Searches for "laptop"
3. Loops through the first 10 search results
4. For each product:
   - Reads the name and price directly from the search results card
   - Clicks into the product page (opens in a new tab) to scrape the description
   - Closes that tab and returns to the results list
5. Saves all 10 products to `laptop_results.json`

## Tech Stack

- **Python 3.13**
- **Playwright** (sync API) — browser automation
- **Chromium** — the browser Playwright drives
- **`json`** (built-in) — for structured output

## Why Playwright instead of `requests` + `BeautifulSoup`

Amazon renders content dynamically with JavaScript and actively blocks simple HTTP scraping. Playwright drives a real browser instance, so it executes JS and behaves like an actual user — clicking, waiting for elements, and handling multi-tab navigation.

## Architecture

```
browser → context → page(s)
```

- One `browser` and one `context` (isolated session) are created.
- Multiple `page` (tab) objects exist within that context — the search-results tab, and a new tab for each product page opened during the loop.
- Data flows: DOM (Amazon page) → Playwright selectors extract text → Python dict → appended to a list → dumped to JSON.

## Key challenges solved

- **New-tab handling**: clicking a product title opens a new browser tab, not the same page — handled with `context.expect_page()` to capture it correctly.
- **Inconsistent listing layouts**: sponsored/Apple listings don't always have the same HTML structure — wrapped extraction in `try/except` so one bad listing doesn't crash the whole run.
- **Tab cleanup**: each product tab is explicitly closed after scraping to avoid piling up open tabs.
- **Stale element references**: re-fetched the product list on every loop iteration instead of reusing one reference.

## How to run

```bash
pip install playwright
playwright install
python amazon_products.py
```

## Sample output (`laptop_results.json`)

```json
{
  "name": "HP 15 Smartchoice, Intel Core Ultra 5 125H...",
  "price": "82,990",
  "url": "https://www.amazon.in/HP-Smartchoice.../dp/B0GWQHQB4T/...",
  "description": "About this item\nProcessor, Memory & Storage:..."
}
```

## Limitations / Future improvements

- Search term ("laptop") is hardcoded — could be made a CLI argument
- No pagination — only scrapes the first results page
- No retry logic on failed selectors
- Runs in visible (non-headless) mode — fine for demo, slower for scale
