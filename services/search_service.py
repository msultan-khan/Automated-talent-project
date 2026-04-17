from typing import Any
from urllib.parse import quote_plus

from utils.text_helpers import normalize_text


def _tokenize_keywords(keywords: str) -> list[str]:
    return [normalize_text(token) for token in (keywords or "").split(",") if normalize_text(token)]


def _build_candidate_search_hits(
    role: str,
    location: str,
    keywords: str,
    job_type: str,
) -> list[dict[str, Any]]:
    keyword_tokens = _tokenize_keywords(keywords)
    keyword_phrase = " ".join(keyword_tokens[:4])
    core_query = normalize_text(f"{role} {location} {job_type} {keyword_phrase} skilled trades jobs")
    encoded_query = quote_plus(core_query)
    location_terms = quote_plus(normalize_text(location))

    return [
        {
            "url": f"https://www.indeed.com/jobs?q={encoded_query}&l={location_terms}",
            "title": f"{role} opportunities in {location}",
            "snippet": "Skilled trades candidate sourcing via Indeed.",
            "query": core_query,
            "source_type": "candidate",
        },
        {
            "url": f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}&location={location_terms}",
            "title": f"{job_type.title()} openings for {role}",
            "snippet": "Candidate sourcing via LinkedIn jobs.",
            "query": core_query,
            "source_type": "candidate",
        },
        {
            "url": f"https://www.ziprecruiter.com/jobs-search?search={encoded_query}&location={location_terms}",
            "title": f"ZipRecruiter listings for {role}",
            "snippet": "Skilled trades candidate sourcing via ZipRecruiter.",
            "query": core_query,
            "source_type": "candidate",
        },
        {
            "url": f"https://www.careerbuilder.com/jobs?keywords={encoded_query}&location={location_terms}",
            "title": f"CareerBuilder listings for {role}",
            "snippet": "Candidate sourcing via CareerBuilder.",
            "query": core_query,
            "source_type": "candidate",
        },
    ]


def _build_project_search_hits(
    role: str,
    location: str,
    keywords: str,
) -> list[dict[str, Any]]:
    keyword_tokens = _tokenize_keywords(keywords)
    project_focus = normalize_text(
        f"US data center construction projects {location} {' '.join(keyword_tokens[:4])}"
    )
    encoded_project_focus = quote_plus(project_focus)
    contractor_focus = quote_plus(
        normalize_text(f"data center general contractor opportunities {location} united states")
    )

    return [
        {
            "url": f"https://www.constructiondive.com/search/?q={encoded_project_focus}",
            "title": "Construction Dive data center project leads",
            "snippet": "News and project updates for U.S. data center construction.",
            "query": project_focus,
            "source_type": "project",
        },
        {
            "url": f"https://www.datacenterdynamics.com/en/search/?q={encoded_project_focus}",
            "title": "Data Center Dynamics project updates",
            "snippet": "U.S. data center build announcements and expansions.",
            "query": project_focus,
            "source_type": "project",
        },
        {
            "url": f"https://www.bisnow.com/search?query={encoded_project_focus}",
            "title": "Bisnow data center development coverage",
            "snippet": "Commercial real estate updates relevant to data center projects.",
            "query": project_focus,
            "source_type": "project",
        },
        {
            "url": f"https://www.enr.com/search?query={contractor_focus}",
            "title": "ENR contractor and construction pipeline signals",
            "snippet": "Engineering and construction publication coverage for projects.",
            "query": project_focus,
            "source_type": "project",
        },
        {
            "url": f"https://www.google.com/search?q={encoded_project_focus}",
            "title": "U.S. data center construction market results",
            "snippet": "Broad project search for additional public announcements.",
            "query": project_focus,
            "source_type": "project",
        },
    ]


def run_search(
    role: str,
    location: str,
    keywords: str,
    job_type: str,
    search_scope: str = "candidates",
) -> list[dict[str, Any]]:
    """
    MVP URL generation for two sourcing streams:
    - candidates (skilled trades talent)
    - projects (U.S. data center construction opportunities)
    """
    if search_scope == "projects":
        return _build_project_search_hits(role=role, location=location, keywords=keywords)
    return _build_candidate_search_hits(role=role, location=location, keywords=keywords, job_type=job_type)
