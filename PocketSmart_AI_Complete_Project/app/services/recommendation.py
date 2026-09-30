import json
from typing import Any
from PIL import Image
from google import genai
from google.genai import types
from ..config import get_settings
from .catalog import candidate_items, search_url
from ..models.schemas import RecommendationResponse


def _client():
    key = get_settings().gemini_api_key
    return genai.Client(api_key=key) if key else None

def _prompt(planner: str, data: dict[str, Any], candidates: list[dict]) -> str:
    return f"""You are PocketSmart AI, a budget planning assistant for India.
Create practical recommendations using ONLY the supplied candidate catalog. Never invent products, prices, or platforms.
Planner: {planner}
User request: {json.dumps(data, ensure_ascii=False)}
Candidate catalog: {json.dumps(candidates, ensure_ascii=False)}

Return ONLY valid JSON matching this shape:
{{"summary":"...","estimated_total":0,"allocations":[{{"category":"...","amount":0,"percentage":0,"note":"..."}}],"recommendations":[{{"name":"...","category":"...","platform":"...","estimated_price":0,"quantity":1,"reason":"...","search_url":"...","priority":"essential|recommended|optional"}}],"tips":["..."]}}
Rules: keep estimated_total <= budget when feasible; prioritize essentials; use integer quantities; use exact candidate prices; do not add candidates not present; percentages should approximately total 100; search_url must be copied from candidates.
"""

def _fallback(planner: str, data: dict[str, Any], candidates: list[dict], image_insight: str | None = None) -> dict:
    budget = float(data["budget"])
    chosen = []
    if planner == "home":
        desired = sum(max(1, int(x.get("quantity", 1))) for x in data["rooms"])
        chosen = candidates[: min(8, max(4, desired))]
    elif planner == "party":
        guests = int(data["guests"])
        for item in candidates:
            item = dict(item)
            if item["category"] in {"catering", "beverages"}:
                item["price"] *= guests
            chosen.append(item)
        chosen = chosen[:6]
    else:
        chosen = candidates[:5]
    rows = []
    total = 0.0
    for c in chosen:
        qty = 1
        if planner == "party" and c["category"] in {"catering", "beverages"}:
            qty = 1
        price = c["price"] * qty
        if total + price <= budget:
            rows.append({"name": c["name"], "category": c["category"], "platform": c["platform"], "estimated_price": round(c["price"],2), "quantity": qty, "reason": "Selected from the built-in candidate catalog to fit the stated budget.", "search_url": search_url(c["platform"], c["name"]), "priority": "essential" if len(rows) < 2 else "recommended"})
            total += price
    categories = {}
    for r in rows:
        categories[r["category"]] = categories.get(r["category"], 0) + r["estimated_price"] * r["quantity"]
    allocations = [{"category": k, "amount": round(v,2), "percentage": round(v / budget * 100, 1), "note": "Catalog-based allocation."} for k,v in categories.items()]
    return {"summary": f"A {planner} plan built around your ₹{budget:,.0f} budget.", "estimated_total": round(total,2), "allocations": allocations, "recommendations": rows, "tips": ["Compare the linked marketplace options before buying.", "Keep a small buffer for delivery, taxes, or last-minute changes."], "image_insight": image_insight}

def _normalise(raw: dict, planner: str, budget: float, candidates: list[dict], image_insight: str | None) -> dict:
    valid = {(c["platform"], c["name"]): c for c in candidates}
    recs = []
    total = 0.0
    for r in raw.get("recommendations", []):
        key = (r.get("platform"), r.get("name"))
        c = valid.get(key)
        if not c:
            continue
        qty = max(1, int(r.get("quantity", 1)))
        price = float(c["price"])
        if total + price * qty > budget:
            continue
        recs.append({"name": c["name"], "category": c["category"], "platform": c["platform"], "estimated_price": price, "quantity": qty, "reason": str(r.get("reason", "Budget-aligned candidate.")), "search_url": search_url(c["platform"], c["name"]), "priority": r.get("priority", "recommended") if r.get("priority") in {"essential","recommended","optional"} else "recommended"})
        total += price * qty
    if not recs:
        return _fallback(planner, {"budget": budget, **({"rooms": []} if planner == "home" else {})}, candidates, image_insight)
    allocations = raw.get("allocations") or [{"category": "recommended items", "amount": round(total,2), "percentage": round(total/budget*100,1), "note": "AI-generated allocation."}]
    return {"summary": str(raw.get("summary", "Budget-aware recommendations generated.")), "estimated_total": round(total,2), "allocations": allocations, "recommendations": recs, "tips": [str(x) for x in raw.get("tips", [])][:6] or ["Compare prices before purchasing."], "image_insight": image_insight}

async def generate(planner: str, data: dict[str, Any], image_bytes: bytes | None = None, image_mime: str | None = None) -> RecommendationResponse:
    candidates = candidate_items(planner, [data.get("style", ""), data.get("occasion", ""), data.get("event_type", "")])
    image_insight = None
    client = _client()
    if client:
        try:
            contents: list[Any] = [_prompt(planner, data, candidates)]
            if image_bytes and image_mime:
                image = Image.open(__import__("io").BytesIO(image_bytes)).convert("RGB")
                contents.append(image)
                contents[0] += "\nAn outfit image is attached. Briefly use visible colors/style only to improve jewelry matching, and include a concise image_insight in the JSON."
            response = client.models.generate_content(model=get_settings().gemini_model, contents=contents, config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.4, max_output_tokens=2500))
            raw = json.loads(response.text)
            result = _normalise(raw, planner, float(data["budget"]), candidates, image_insight)
            result["image_insight"] = raw.get("image_insight") or image_insight
            return RecommendationResponse(planner=planner, budget=float(data["budget"]), remaining_budget=max(0, float(data["budget"]) - result["estimated_total"]), ai_powered=True, **result)
        except Exception:
            pass
    result = _fallback(planner, data, candidates, image_insight)
    return RecommendationResponse(planner=planner, budget=float(data["budget"]), remaining_budget=max(0, float(data["budget"]) - result["estimated_total"]), ai_powered=False, **result)
