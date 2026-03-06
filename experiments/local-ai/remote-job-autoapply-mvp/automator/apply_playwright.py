from pathlib import Path
from playwright.sync_api import sync_playwright


def submit_application(
    application_url: str,
    full_name: str,
    email: str,
    resume_path: Path,
    cover_letter_path: Path,
    dry_run: bool = True,
) -> bool:
    """
    Generic best-effort form submission.
    Keep dry_run=True by default to avoid accidental spam and policy violations.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(application_url, wait_until="domcontentloaded", timeout=60_000)

        # Heuristic field mapping across common ATS forms.
        for selector in ["input[name*='name']", "input[id*='name']"]:
            if page.locator(selector).count() > 0:
                page.locator(selector).first.fill(full_name)
                break

        for selector in ["input[type='email']", "input[name*='email']"]:
            if page.locator(selector).count() > 0:
                page.locator(selector).first.fill(email)
                break

        for selector in ["input[type='file']", "input[name*='resume']"]:
            if page.locator(selector).count() > 0:
                page.locator(selector).first.set_input_files(str(resume_path))
                break

        if page.locator("textarea").count() > 0:
            page.locator("textarea").first.fill(cover_letter_path.read_text(encoding="utf-8"))

        if not dry_run:
            for selector in ["button:has-text('Submit')", "input[type='submit']"]:
                if page.locator(selector).count() > 0:
                    page.locator(selector).first.click()
                    break

        browser.close()
    return True
