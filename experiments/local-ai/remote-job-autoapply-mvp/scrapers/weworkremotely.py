import requests
from bs4 import BeautifulSoup
from models import JobListing


WWR_URL = "https://weworkremotely.com/remote-jobs/search?term=python"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_weworkremotely_jobs(limit: int = 20) -> list[JobListing]:
    try:
        response = requests.get(WWR_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        # Some regions/environments are blocked by WWR (often HTTP 403).
        # Return an empty list so the full pipeline can continue with other sources.
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    jobs: list[JobListing] = []
    for li in soup.select("section.jobs li"):
        link_tag = li.select_one("a")
        company = li.select_one("span.company")
        title = li.select_one("span.title")
        region = li.select_one("span.region")
        if not link_tag or not title:
            continue

        href = link_tag.get("href", "")
        full_link = f"https://weworkremotely.com{href}" if href.startswith("/") else href

        jobs.append(
            JobListing(
                source="WeWorkRemotely",
                company=company.text.strip() if company else "Unknown",
                title=title.text.strip(),
                description="See application page for full description.",
                location=region.text.strip() if region else "Remote",
                application_link=full_link,
            )
        )
        if len(jobs) >= limit:
            break
    return jobs
