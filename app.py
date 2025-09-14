# app.py
"""
FastAPI backend providing:
- /search -> product search by tags/category/price
- /product/{pid} -> product detail
- /conversation -> start new conversation
- /conversation/{conv_id}/message -> post user message; runs interest scoring and returns matches
- /admin/* -> basic product CRUD (protected by a simple token param)
- /analytics -> simple statistics
"""
from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json, re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
import datetime

# --- DB models (same as db_setup but minimal here) ---
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    product_id = Column(String, unique=True, index=True)
    name = Column(String)
    category = Column(String)
    description = Column(Text)
    ingredients = Column(Text)
    price = Column(Float)
    calories = Column(Integer)
    prep_time = Column(String)
    dietary_tags = Column(Text)
    mood_tags = Column(Text)
    allergens = Column(Text)
    popularity_score = Column(Integer)
    chef_special = Column(Boolean)
    limited_time = Column(Boolean)
    spice_level = Column(Integer)
    image_prompt = Column(Text)
    image_url = Column(Text)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_name = Column(String, default="guest")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, index=True)
    sender = Column(String)  # "user" or "bot"
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    interest_score = Column(Integer, nullable=True)

# --- DB setup ---
engine = create_engine("sqlite:///products.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

# --- FastAPI app ---
app = FastAPI(title="FoodieBot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic models for requests/responses ---
class SearchResponse(BaseModel):
    product_id: str
    name: str
    category: Optional[str]
    price: float
    popularity_score: int
    spice_level: int
    image_url: Optional[str]
    score: float

class StartConvResponse(BaseModel):
    conversation_id: int

class MessageRequest(BaseModel):
    text: str
    user_name: Optional[str] = "guest"
    budget: Optional[float] = None

class MessageResponse(BaseModel):
    bot_text: str
    interest_score: int
    matches: List[SearchResponse]

# --- Interest score factors (from your doc) ---
ENGAGEMENT_FACTORS = {
    "specific_preferences": 15,
    "dietary_restrictions": 10,
    "budget_mention": 5,
    "mood_indication": 20,
    "question_asking": 10,
    "enthusiasm_words": 8,
    "price_inquiry": 25,
    "order_intent": 30,
}
NEGATIVE_FACTORS = {
    "hesitation": -10,
    "budget_concern": -15,
    "dietary_conflict": -20,
    "rejection": -25,
    "delay_response": -5
}

# --- Utilities: simple NLU heuristics (rules) ---
def extract_signals(text):
    text_l = text.lower()
    signals = {}
    # specific preferences: detect keywords like "spicy", "korean", "burger", "tacos", etc
    keywords = ["spicy","korean","burger","taco","tacos","pizza","vegan","vegetarian","gluten-free","gluten free","dessert","salad","breakfast","cheap","under $"]
    if any(k in text_l for k in keywords):
        signals["specific_preferences"] = True

    # dietary restrictions
    if any(word in text_l for word in ["vegetarian","vegan","no meat","no pork","no beef","lactose","dairy-free","gluten-free","allergy","allergic"]):
        signals["dietary_restrictions"] = True

    # budget mention (simple)
    m = re.search(r"\bunder\s*\$?(\d+)", text_l)
    if m:
        signals["budget_mention"] = float(m.group(1))
    elif re.search(r"\$\d+", text_l):
        signals["price_inquiry"] = True

    # mood
    if any(word in text_l for word in ["adventurous","comfort","cheer","indulgent","healthy"]):
        signals["mood_indication"] = True

    # question
    if "?" in text_l:
        signals["question_asking"] = True

    # enthusiasm words
    if any(word in text_l for word in ["amazing","love","perfect","awesome","great","delicious","yum"]):
        signals["enthusiasm_words"] = True

    # order intent
    if any(phrase in text_l for phrase in ["add to cart","i'll take","i will take","order now","i want to order","buy it","add it"]):
        signals["order_intent"] = True

    # hesitation & rejection
    if any(phrase in text_l for phrase in ["maybe","not sure","i don't know","dont know"]):
        signals["hesitation"] = True
    if any(phrase in text_l for phrase in ["too expensive","not for me","i don't like that","i dont like that"]):
        signals["rejection"] = True

    # budget concern
    if any(phrase in text_l for phrase in ["too expensive","costly","expensive"]):
        signals["budget_concern"] = True

    return signals

def compute_interest(signals):
    score = 0
    # positive additions
    if signals.get("specific_preferences"):
        score += ENGAGEMENT_FACTORS["specific_preferences"]
    if signals.get("dietary_restrictions"):
        score += ENGAGEMENT_FACTORS["dietary_restrictions"]
    if "budget_mention" in signals and isinstance(signals["budget_mention"], (int,float)):
        score += ENGAGEMENT_FACTORS["budget_mention"]
    if signals.get("mood_indication"):
        score += ENGAGEMENT_FACTORS["mood_indication"]
    if signals.get("question_asking"):
        score += ENGAGEMENT_FACTORS["question_asking"]
    if signals.get("enthusiasm_words"):
        score += ENGAGEMENT_FACTORS["enthusiasm_words"]
    if signals.get("price_inquiry"):
        score += ENGAGEMENT_FACTORS["price_inquiry"]
    if signals.get("order_intent"):
        score += ENGAGEMENT_FACTORS["order_intent"]

    # negatives
    if signals.get("hesitation"):
        score += NEGATIVE_FACTORS["hesitation"]
    if signals.get("budget_concern"):
        score += NEGATIVE_FACTORS["budget_concern"]
    if signals.get("rejection"):
        score += NEGATIVE_FACTORS["rejection"]

    # normalize to 0-100
    if score < 0:
        score = 0
    if score > 100:
        score = 100
    return int(score)

# --- Simple product scoring by compatibility ---
def product_match_score(product: Product, signals):
    # convert tags stored as JSON strings
    try:
        mood_tags = json.loads(product.mood_tags or "[]")
    except:
        mood_tags = []
    try:
        dietary_tags = json.loads(product.dietary_tags or "[]")
    except:
        dietary_tags = []

    score = 0.0
    # match mood
    if signals.get("mood_indication"):
        score += 10
    # match dietary: penalize products that conflict
    if signals.get("dietary_restrictions"):
        # if product has dietary tags that conflict (e.g., contains_gluten) penalize
        if "contains_gluten" in dietary_tags or "contains_dairy" in dietary_tags:
            score -= 20
        else:
            score += 15

    # specific keywords matching product name/category
    stext = ""
    if signals.get("specific_preferences"):
        stext = " ".join([k for k in ["spicy","korean","burger","taco","pizza","fried","chicken","vegan","vegetarian","salad"]])
    # naive match: if name/category contains any of the user's tokens
    # (We simplified: real implementation would use semantic matching / embeddings)
    for token in ["spicy","korean","burger","taco","pizza","chicken","vegan","vegetarian","salad"]:
        if token in (product.name or "").lower() or token in (product.category or "").lower():
            score += 8

    # price bias for budget_mention
    if "budget_mention" in signals and isinstance(signals["budget_mention"], (int,float)):
        if product.price <= signals["budget_mention"]:
            score += 12
        else:
            score -= 8

    # popularity contributes
    score += (product.popularity_score or 0) / 20.0  # scale popularity

    # spice preference: if user mentions 'spicy', boost spicy items
    # we already matched keywords above; additionally use spice_level
    if "spicy" in (stext):
        score += (product.spice_level or 0) * 0.3

    # final clamp
    if score < 0:
        score = 0
    return score

# --- API endpoints ---
@app.post("/conversation", response_model=StartConvResponse)
def start_conversation(user_name: Optional[str] = Query("guest")):
    db = SessionLocal()
    conv = Conversation(user_name=user_name)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"conversation_id": conv.id}

@app.post("/conversation/{conv_id}/message", response_model=MessageResponse)
def post_message(conv_id: int, req: MessageRequest):
    db = SessionLocal()
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # store user message
    m = Message(conversation_id=conv_id, sender="user", text=req.text)
    db.add(m)
    db.commit()
    db.refresh(m)

    # run NLU to extract signals and compute interest
    signals = extract_signals(req.text)
    interest = compute_interest(signals)

    # find candidate products and score them
    products = db.query(Product).all()
    scored = []
    for p in products:
        s = product_match_score(p, signals)
        if s > 0:
            scored.append((s, p))
    # sort descending
    scored.sort(key=lambda x: x[0], reverse=True)
    # prepare top 6 results
    matches = []
    for s, p in scored[:6]:
        matches.append({
            "product_id": p.product_id,
            "name": p.name,
            "category": p.category,
            "price": p.price,
            "popularity_score": p.popularity_score,
            "spice_level": p.spice_level,
            "image_url": p.image_url,
            "score": round(s, 2)
        })

    # bot message (simple templated response)
    if len(matches) == 0:
        bot_text = "I couldn't find a match right now — can you tell me more about what you'd like? (price, type, or dietary needs)"
    else:
        bot_text = f"I found {len(matches)} items that match your request. Here are the top picks. Interest score: {interest}%"

    bot_msg = Message(conversation_id=conv_id, sender="bot", text=bot_text, interest_score=interest)
    db.add(bot_msg)
    db.commit()

    # return
    return {
        "bot_text": bot_text,
        "interest_score": interest,
        "matches": matches
    }

@app.get("/search", response_model=List[SearchResponse])
def search_products(q: Optional[str] = Query(None), category: Optional[str] = None, max_price: Optional[float] = None):
    db = SessionLocal()
    # naive search
    products = db.query(Product).all()
    results = []
    for p in products:
        if category and (p.category or "").lower() != category.lower():
            continue
        if max_price and p.price > max_price:
            continue
        if q:
            if q.lower() not in (p.name or "").lower() and q.lower() not in (p.description or "").lower():
                continue
        # construct score = popularity + simple relevance
        score = (p.popularity_score or 0) / 10.0
        results.append({
            "product_id": p.product_id,
            "name": p.name,
            "category": p.category,
            "price": p.price,
            "popularity_score": p.popularity_score,
            "spice_level": p.spice_level,
            "image_url": p.image_url,
            "score": score
        })
    # sort by score desc
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:30]

# --- admin crud (protected by a simple token passed as query param) ---
ADMIN_TOKEN = "letmein"  # change this for real deployments

class ProductIn(BaseModel):
    product_id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = []
    price: float
    calories: Optional[int] = None
    prep_time: Optional[str] = None
    dietary_tags: Optional[List[str]] = []
    mood_tags: Optional[List[str]] = []
    allergens: Optional[List[str]] = []
    popularity_score: Optional[int] = 50
    chef_special: Optional[bool] = False
    limited_time: Optional[bool] = False
    spice_level: Optional[int] = 0
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None

@app.post("/admin/product")
def admin_create_product(p: ProductIn, token: str = Query(...)):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    db = SessionLocal()
    prod = Product(
        product_id=p.product_id,
        name=p.name,
        category=p.category,
        description=p.description,
        ingredients=json.dumps(p.ingredients),
        price=p.price,
        calories=p.calories,
        prep_time=p.prep_time,
        dietary_tags=json.dumps(p.dietary_tags),
        mood_tags=json.dumps(p.mood_tags),
        allergens=json.dumps(p.allergens),
        popularity_score=p.popularity_score,
        chef_special=p.chef_special,
        limited_time=p.limited_time,
        spice_level=p.spice_level,
        image_prompt=p.image_prompt,
        image_url=p.image_url
    )
    db.add(prod)
    db.commit()
    return {"status": "created", "product_id": p.product_id}

@app.get("/analytics")
def analytics():
    db = SessionLocal()
    total_products = db.query(Product).count()
    total_convos = db.query(Conversation).count()
    total_msgs = db.query(Message).count()
    # simple product popularity top 5
    prods = db.query(Product).order_by(Product.popularity_score.desc()).limit(5).all()
    top = [{"product_id": p.product_id, "name": p.name, "popularity_score": p.popularity_score} for p in prods]
    return {"total_products": total_products, "total_conversations": total_convos, "total_messages": total_msgs, "top_products": top}
