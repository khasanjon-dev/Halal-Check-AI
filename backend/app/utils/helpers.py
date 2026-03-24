def normalize_halal_status(is_halal) -> str:
    if isinstance(is_halal, bool):
        return "true" if is_halal else "false"
    elif isinstance(is_halal, str):
        return is_halal.lower()
    return "doubtful"


def normalize_edible_status(is_edible) -> bool:
    if isinstance(is_edible, bool):
        return is_edible
    elif isinstance(is_edible, str):
        return is_edible.lower() in ["true", "yes", "1"]
    return False


def patch_analysis_result(result: dict, fallback_name: str) -> dict:
    result = result or {}
    result.setdefault("product_name", fallback_name[:50])
    result.setdefault("is_halal", "doubtful")
    result.setdefault("is_edible", False)
    result.setdefault("ingredients_analysis", [])
    result.setdefault("overall_summary", "")
    result.setdefault("category", None)
    if not result.get("is_edible", False):
        result["is_halal"] = "doubtful"
    return result
