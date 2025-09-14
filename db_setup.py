# db_setup.py
"""
Creates SQLite DB (products.db) and imports products.json into a products table.
Also creates tables for conversations and messages for storing chat history.
"""
import json
from sqlalchemy import (create_engine, Column, Integer, String, Float, Boolean, Text, DateTime)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    product_id = Column(String, unique=True, index=True)
    name = Column(String)
    category = Column(String)
    description = Column(Text)
    ingredients = Column(Text)      # store lists as JSON string
    price = Column(Float)
    calories = Column(Integer)
    prep_time = Column(String)
    dietary_tags = Column(Text)     # JSON string
    mood_tags = Column(Text)        # JSON string
    allergens = Column(Text)        # JSON string
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
    interest_score = Column(Integer, nullable=True)  # store score when computed

def main():
    engine = create_engine("sqlite:///products.db", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Read products.json and insert
    with open("products.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    # Insert (idempotent: skip if product exists)
    for p in products:
        exists = session.query(Product).filter_by(product_id=p["product_id"]).first()
        if exists:
            continue
        prod = Product(
            product_id=p["product_id"],
            name=p["name"],
            category=p.get("category"),
            description=p.get("description"),
            ingredients=json.dumps(p.get("ingredients", [])),
            price=p.get("price", 0.0),
            calories=p.get("calories", None),
            prep_time=p.get("prep_time"),
            dietary_tags=json.dumps(p.get("dietary_tags", [])),
            mood_tags=json.dumps(p.get("mood_tags", [])),
            allergens=json.dumps(p.get("allergens", [])),
            popularity_score=int(p.get("popularity_score", 0)),
            chef_special=bool(p.get("chef_special", False)),
            limited_time=bool(p.get("limited_time", False)),
            spice_level=int(p.get("spice_level", 0)),
            image_prompt=p.get("image_prompt"),
            image_url=p.get("image_url")
        )
        session.add(prod)
    session.commit()
    print("Imported products into products.db")

if __name__ == "__main__":
    main()
