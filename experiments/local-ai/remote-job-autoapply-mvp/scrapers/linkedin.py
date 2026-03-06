import requests
from bs4 import BeautifulSoup
from models import JobListing


# Public LinkedIn guest endpoint (no auth/session required).
LINKEDIN_GUEST_URL = (
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    "?keywords=python&location=Remote&f_WT=2"
)


def fetch_linkedin_jobs(limit: int = 20) -> list[JobListing]:
    response = requests.get(
        LINKEDIN_GUEST_URL,
        headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    jobs: list[JobListing] = []
    for card in soup.select("li"):
        title_tag = card.select_one("h3")
        company_tag = card.select_one("h4")
        location_tag = card.select_one("span.job-search-card__location")
        link_tag = card.select_one("a.base-card__full-link")

        if not title_tag or not link_tag:
            continue

        jobs.append(
            JobListing(
                source="LinkedIn",
                company=company_tag.text.strip() if company_tag else "Unknown",
                title=title_tag.text.strip(),
                description="See LinkedIn job page for full details.",
                location=location_tag.text.strip() if location_tag else "Remote",
                application_link=link_tag.get("href"),
            )
        )
        if len(jobs) >= limit:
            break
    return jobs
