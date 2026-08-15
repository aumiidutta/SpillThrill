import random


def pick_challenge(items, exclude_ids):
    if not items:
        raise ValueError("No challenges available")

    exclude_set = {str(x) for x in exclude_ids}
    remaining = [item for item in items if str(item.get("id")) not in exclude_set]

    reset_happened = False
    if not remaining:
        remaining = items
        reset_happened = True

    chosen = random.choice(remaining)
    return chosen, reset_happened
