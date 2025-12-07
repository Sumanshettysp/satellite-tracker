from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.heavens-above.com/ChangeLocation.aspx")

    print("Page loaded!")

    try:
        page.locator('input[name="Lat"]').wait_for()
        print("Latitude input found!")
    except:
        print("Latitude input NOT found!")

    browser.close()
