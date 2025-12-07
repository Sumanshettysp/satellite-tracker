from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    url = "https://www.n2yo.com/passes/?s=25544"   # ISS passes page
    page.goto(url)

    # ⭐ Replace networkidle wait with this
    page.wait_for_selector("table")

    print("\n=== TABLE HEADER COLUMNS ===")
    headers = page.locator("table thead tr th")
    for i in range(headers.count()):
        print(i, headers.nth(i).inner_text())

    print("\n=== FIRST ROW COLUMNS ===")
    row = page.locator("table tbody tr").first
    cells = row.locator("td")
    for i in range(cells.count()):
        print(i, repr(cells.nth(i).inner_text()))

    browser.close()

