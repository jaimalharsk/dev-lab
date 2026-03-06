import requests
from bs4 import BeautifulSoup
from models import JobListing


WWR_URL = "https://weworkremotely.com/remote-jobs/search?term=python"


def fetch_weworkremotely_jobs(limit: int = 20) -> list[JobListing]:
    response = requests.get(WWR_URL, timeout=30)
    response.raise_for_status()
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
