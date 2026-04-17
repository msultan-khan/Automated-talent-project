from utils.text_helpers import normalize_text


def score_content(
    extracted_text: str,
    role: str,
    location: str,
    keywords: str,
    search_scope: str = "candidates",
) -> dict[str, object]:
    text = normalize_text((extracted_text or "").lower())
    role_l = role.lower()
    location_l = location.lower()

    keyword_list = [k.strip().lower() for k in keywords.split(",") if k.strip()]
    keyword_hits = sum(1 for kw in keyword_list if kw in text)

    match_role = role_l in text if role_l else False
    match_location = location_l in text if location_l else False

    project_terms = ["data center", "construction", "contractor", "build", "expansion", "megawatt"]
    project_hits = sum(1 for term in project_terms if term in text)

    base_score = (4 if match_role else 0) + (3 if match_location else 0) + min(keyword_hits, 3)
    if search_scope == "projects":
        raw_score = min(base_score + min(project_hits, 3), 10)
    else:
        raw_score = base_score
    score = min(raw_score, 10)

    reasons = []
    if match_role:
        reasons.append(f"contains role '{role}'")
    if match_location:
        reasons.append(f"contains location '{location}'")
    if keyword_hits:
        reasons.append(f"matches {keyword_hits} keyword(s)")
    if search_scope == "projects" and project_hits:
        reasons.append(f"matches {project_hits} data-center project signal(s)")
    if not reasons:
        reasons.append("low semantic overlap with search intent")

    return {
        "match_role": match_role,
        "match_location": match_location,
        "score": score,
        "short_reason": "; ".join(reasons),
    }
