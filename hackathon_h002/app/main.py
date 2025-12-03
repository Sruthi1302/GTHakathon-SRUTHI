from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import ChatRequest, ChatResponse
from .pii_masker import redact_pii
from .geolocator import find_nearest_store
from .rag_engine import SimpleRAG
from .llm_engine import generate_reply

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List


app = FastAPI(title="H-002 Hyper-Personalized Customer Support Bot")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


customers_df = pd.read_csv("data/customers.csv")
stores_df = pd.read_csv("data/stores.csv")
inventory_df = pd.read_csv("data/inventory.csv")
offers_df = pd.read_csv("data/offers.csv")


customers = customers_df.to_dict(orient="records")
stores = stores_df.to_dict(orient="records")
inventory = inventory_df.to_dict(orient="records")
offers = offers_df.to_dict(orient="records")


rag = SimpleRAG()


def load_rag_docs():
    docs = []
    for r in offers:
        docs.append(
            {
                "id": f"offer_{r.get('offer_id')}",
                "text": r.get("description", ""),
                "meta": {
                    "type": "offer",
                    "store_id": r.get("store_id"),
                    "product": r.get("product"),
                },
            }
        )
    return docs


rag.build_index(load_rag_docs())


def find_customer(user_id: str) -> Dict[str, Any]:
    for c in customers:
        if str(c.get("user_id")) == str(user_id):
            return c
    return {}


def mark_store_open_status(store: Dict[str, Any]) -> Dict[str, Any]:
    if not store:
        return store
    now = datetime.now().time()
    try:
        open_t = datetime.strptime(store["open_time"], "%H:%M").time()
        close_t = datetime.strptime(store["close_time"], "%H:%M").time()
        is_open = open_t <= now <= close_t
    except Exception:
        is_open = False
    store = {k: v for k, v in store.items()}
    store["is_open"] = is_open
    return store


def filter_inventory_for_store(store_id: str, user_message: str) -> List[Dict[str, Any]]:
    user_msg_lower = user_message.lower()
    relevant = []
    for item in inventory:
        if str(item.get("store_id")) != str(store_id):
            continue
        if item.get("in_stock", 0) and (
            item["product"].lower() in user_msg_lower
            or item["size"].lower() in user_msg_lower
            or "stock" in user_msg_lower
            or "available" in user_msg_lower
        ):
            relevant.append(item)
    return relevant


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    customer = find_customer(req.user_id)

    selected_store = None
    if req.location and "lat" in req.location and "lon" in req.location:
        selected_store = find_nearest_store(req.location["lat"], req.location["lon"], stores)
        if selected_store:
            selected_store = mark_store_open_status(selected_store)

    rag_docs = rag.query(req.message, top_k=3)

    store_offers_docs = []
    if selected_store:
        for d in rag_docs:
            if d["meta"].get("store_id") == selected_store.get("store_id") or d["meta"].get("store_id") == "ALL":
                store_offers_docs.append(d)
        if not store_offers_docs:
            store_offers_docs = rag_docs
    else:
        store_offers_docs = rag_docs

    inventory_items = []
    if selected_store:
        inventory_items = filter_inventory_for_store(selected_store["store_id"], req.message)

    debug_context = {
        "customer": customer,
        "selected_store": selected_store,
        "rag_docs": store_offers_docs,
        "inventory_items": inventory_items,
    }

    context_str = f"""
    Customer: {customer}
    Store: {selected_store}
    Offers: {store_offers_docs}
    Inventory: {inventory_items}
    User message: {req.message}
    """
    _ = redact_pii(context_str)

    reply_text = generate_reply(
        user_message=req.message,
        customer=customer,
        store=selected_store,
        offers=store_offers_docs,
        inventory_items=inventory_items,
    )

    safe_reply_text = redact_pii(reply_text)

    return ChatResponse(
        reply=safe_reply_text,
        used_store=selected_store.get("name") if selected_store else None,
        debug_context=debug_context,
    )
