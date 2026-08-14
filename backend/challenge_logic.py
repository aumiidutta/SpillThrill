"""
Pure logic for picking a challenge, kept separate from any AWS/boto3 code
so it can be unit-tested without needing a live DynamoDB connection.
"""
import random


def pick_challenge(items, exclude_ids):
    """
    Pick a random challenge from `items` that is not in `exclude_ids`.

    items: list of dicts, each with at least an "id" key (str or int)
    exclude_ids: iterable of ids (str) already shown to this user

    Returns: (chosen_item, reset_happened)
      chosen_item   -> the dict that was picked
      reset_happened -> True if every item had already been seen, so we
                         wrapped around and the caller should clear its
                         "seen" list (except for the id we just returned)

    Raises ValueError if items is empty.
    """
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
