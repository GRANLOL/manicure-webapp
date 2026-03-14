import keyboards


def build_category_list_text(categories, empty_text: str = "Список категорий пуст.") -> str:
    if not categories:
        return empty_text

    lines = ["Список категорий:"]
    tree = keyboards.build_category_tree(categories)
    for category, depth in tree:
        name = category["name"] if isinstance(category, dict) else category[1]
        prefix = "  " * depth + ("↳ " if depth > 0 else "📁 ")
        lines.append(f"{prefix}{name}")
    return "\n".join(lines)


def filter_valid_parent_categories(categories, blocked_ids: set[int]) -> list[dict]:
    return [category for category in categories if category["id"] not in blocked_ids]
