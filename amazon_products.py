from playwright.sync_api import sync_playwright
import json

RESULTS = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Open Amazon
    page.goto("https://www.amazon.in/")

    # Search for laptop
    page.locator("#twotabsearchtextbox").fill("laptop")
    page.locator("#nav-search-submit-button").click()

    # Wait for products
    page.wait_for_selector("[data-component-type='s-search-result']")

    products = page.locator("[data-component-type='s-search-result']")
    total = products.count()
    print("Number of products found:", total)

    # How many to scrape
    LIMIT = min(10, total)

    for i in range(LIMIT):
        print(f"\n{'='*60}")
        print(f"Product {i+1} of {LIMIT}")
        print(f"{'='*60}")

        # Re-fetch the list each loop — after opening/closing tabs the
        # old locator handles can go stale on some Amazon layouts.
        products = page.locator("[data-component-type='s-search-result']")
        product = products.nth(i)

        # Name
        try:
            name = product.locator("h2").inner_text()
        except Exception:
            name = "N/A"

        # Price
        try:
            price = product.locator(".a-price-whole").first.inner_text()
        except Exception:
            price = "N/A"

        print("Name:", name)
        print("Price:", "₹" + price if price != "N/A" else "N/A")

        # Open product page — Amazon usually opens a NEW TAB
        description = "N/A"
        product_url = "N/A"
        try:
            try:
                with context.expect_page(timeout=5000) as new_page_info:
                    product.locator("h2").click()
                product_page = new_page_info.value
            except Exception:
                # No new tab opened — same page navigated instead
                product_page = page

            product_page.wait_for_load_state("domcontentloaded")
            product_url = product_page.url

            try:
                product_page.wait_for_selector("#feature-bullets", timeout=8000)
                description = product_page.locator("#feature-bullets").inner_text()
            except Exception:
                description = "No 'About this item' section found."

        except Exception as e:
            print("Error opening product page:", e)

        finally:
            # Close the product tab if it's a separate tab, keep search page open
            if product_page != page:
                product_page.close()

        print("URL:", product_url)
        print("Description:")
        print(description)

        RESULTS.append({
            "name": name,
            "price": price,
            "url": product_url,
            "description": description
        })

    print(f"\n{'='*60}")
    print(f"Scraped {len(RESULTS)} products")
    print(f"{'='*60}")

    # Save to JSON file
    with open("laptop_results.json", "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, ensure_ascii=False, indent=2)
    print("\nSaved results to laptop_results.json")

    input("\nPress ENTER to close the browser...")
    browser.close()