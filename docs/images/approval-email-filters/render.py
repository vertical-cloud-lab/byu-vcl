"""Render each mock-up in mockups.html to its own PNG, named after the section id.

    pip install playwright
    python docs/images/approval-email-filters/render.py

Uses the system Chrome (channel="chrome"), so no `playwright install` is needed.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    page = browser.new_page(viewport={"width": 960, "height": 800}, device_scale_factor=2)
    page.goto((HERE / "mockups.html").as_uri())
    for frame in page.locator("section.frame").all():
        name = frame.get_attribute("id")
        frame.screenshot(path=HERE / f"{name}.png")
        print(f"{name}.png")
    browser.close()
