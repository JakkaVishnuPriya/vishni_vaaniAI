import re

def validate_citations(answer: str, sources: list[dict]) -> tuple[bool, list[str]]:
    issues = []
    if not sources:
        issues.append("No supporting passages were retrieved.")
    citation_pattern = r"\[(\d+)\]"
    cited = {int(x) for x in re.findall(citation_pattern, answer)}
    valid = set(range(1, len(sources) + 1))
    if not cited:
        issues.append("The answer contains no numbered source citations.")
    if cited - valid:
        issues.append("The answer contains citation numbers that do not exist.")
    return not issues, issues
