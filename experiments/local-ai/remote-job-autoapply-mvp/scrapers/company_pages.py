import requests
from bs4 import BeautifulSoup
from models import JobListing


def fetch_company_careers_jobs(career_urls: list[str], limit_per_company: int = 5) -> list[JobListing]:
    jobs: list[JobListing] = []
    for url in career_urls:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
        except requests.RequestException:
            continue

        anchors = soup.select("a[href*='job'], a[href*='career'], a[href*='position']")
        company_name = url.split("//")[-1].split(".")[0].capitalize()

        count = 0
        for a in anchors:
            title = a.get_text(strip=True)
            href = a.get("href", "")
            if not title or len(title) < 5:
                continue
            full_link = href if href.startswith("http") else f"{url.rstrip('/')}/{href.lstrip('/')}"
            jobs.append(
                JobListing(
                    source="CompanyCareerPage",
                    company=company_name,
                    title=title,
                    description="Visit job page for details.",
                    location="Remote/Unknown",
                    application_link=full_link,
                )
            )
            count += 1
            if count >= limit_per_company:
                break
    return jobs
