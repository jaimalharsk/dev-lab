import requests
from models import JobListing


REMOTE_OK_URL = "https://remoteok.com/api"


def fetch_remoteok_jobs(limit: int = 20) -> list[JobListing]:
    response = requests.get(REMOTE_OK_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    data = response.json()[1 : limit + 1]  # first item is metadata

    jobs: list[JobListing] = []
    for item in data:
        jobs.append(
            JobListing(
                source="RemoteOK",
                company=item.get("company", "Unknown"),
                title=item.get("position", "Unknown"),
                description=item.get("description", ""),
                location=item.get("location", "Remote"),
                application_link=f"https://remoteok.com/remote-jobs/{item.get('id')}",
            )
        )
    return jobs
