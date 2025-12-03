from typing import Dict, List, Optional


def generate_reply(
    user_message: str,
    customer: Optional[Dict],
    store: Optional[Dict],
    offers: List[Dict],
    inventory_items: List[Dict],
) -> str:
    """Simple rule-based reply generator (local, no external LLM)."""

    user_message_lower = user_message.lower()
    name = customer.get("name") if customer else "there"
    fav_drink = customer.get("favorite_drink") if customer else None

    # Store description
    if store:
        distance = store.get("distance_in_m")
        distance_text = f"{int(distance)}m" if distance is not None else "nearby"
        store_status = "OPEN" if store.get("is_open") else "CLOSED"
        store_part = (
            f"The nearest store is {store.get('name')} about {distance_text} away. "
            f"It is currently {store_status}."
        )
    else:
        store_part = "I couldn't find a nearby store."

    # Offers
    if offers:
        offers_lines = []
        for off in offers:
            desc = off.get("text") or off.get("description") or ""
            offers_lines.append(f"- {desc}")
        offers_text = "Here are some offers for you:\n" + "\n".join(offers_lines)
    else:
        offers_text = "There are no special offers I can find right now."

    # Inventory text
    inv_text = ""
    if inventory_items:
        inv_desc = []
        for it in inventory_items:
            inv_desc.append(f"{it.get('product')} ({it.get('size')})")
        inv_text = "We have these relevant items in stock: " + ", ".join(inv_desc) + "."

    # Suggestions
    suggestion = ""
    if "cold" in user_message_lower and fav_drink:
        suggestion = (
            f"Since you're feeling cold and you often enjoy {fav_drink}, "
            f"you could come inside and warm up with one!"
        )
    elif "cold" in user_message_lower:
        suggestion = "Since you're feeling cold, you might like a hot drink like Hot Cocoa or a Latte."
    elif "offer" in user_message_lower or "coupon" in user_message_lower:
        suggestion = "Here are the offers I can see for you right now."
    elif "open" in user_message_lower or "timing" in user_message_lower:
        suggestion = "Let me tell you about the nearest store and its timings."

    parts = [
        f"Hi {name}! 👋",
        suggestion,
        store_part,
        offers_text,
        inv_text,
    ]
    parts = [p for p in parts if p]
    return "\n\n".join(parts)
