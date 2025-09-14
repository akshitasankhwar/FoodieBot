🍔 FoodieBot — Fast-Food Recommendation & Chat System
Project Overview

FoodieBot is an interactive system that allows users to chat with a recommendation bot, search products, and view personalized suggestions based on preferences, dietary restrictions, budget, and mood. It also provides an admin panel and basic analytics.

Features:

Live chat with FoodieBot

Product search and filtering

Interest scoring of user messages

Admin panel to create products

Analytics: top products, total conversations, messages

Project Structure

Files:

generate_products.py → Generates 100 sample fast-food products into products.json.

db_setup.py → Creates SQLite DB (products.db) and populates products table.

app.py → FastAPI backend with chat, search, admin, analytics endpoints.

streamlit_app.py → Streamlit frontend UI for chat, search, admin, analytics.

products.json → Generated sample product data.

products.db → SQLite database created by db_setup.py.

requirements.txt → Python dependencies.

Setup Instructions

Clone the project

git clone https://github.com/akshitasankhwar/FoodieBot.git
cd FoodieBot


Install dependencies

pip install -r requirements.txt


Generate sample products

python generate_products.py


Creates products.json with 100 sample items.

Setup the database

python db_setup.py


Creates products.db and populates the products table. Also sets up tables for conversations and messages.

Run FastAPI backend

uvicorn app:app --reload


API will be available at http://localhost:8000.

Run Streamlit frontend

streamlit run streamlit_app.py


Open the local URL provided by Streamlit to interact with the UI.

How It Works
Chat System

Users start a conversation via the sidebar.

Messages are sent to the FastAPI backend.

Signals are extracted from user text:

Preferences (spicy, vegan, type of food)

Mood

Budget

Dietary restrictions

Interest score is computed.

Products are ranked and top suggestions returned.

Search / Filter

Search by name or description.

Filter by category or max price.

Results include popularity score and relevance.

Admin Panel

Token-protected (default token: letmein).

Create new products with basic details.

Analytics

Total products

Total conversations

Total messages

Top 5 products by popularity

Script Explanations

generate_products.py

Generates 100 fake fast-food products with randomized attributes.

Outputs products.json.

db_setup.py

Creates SQLite database products.db.

Imports products from products.json.

Sets up tables for conversations and messages.

app.py

FastAPI backend endpoints:

/conversation → Start conversation

/conversation/{id}/message → Send message & get product matches

/search → Search products

/admin/product → Create product (token required)

/analytics → Basic stats

streamlit_app.py

Streamlit frontend interface:

Chat with bot

Search/filter products

Admin panel for product creation

Analytics tab

Usage Example

Start backend:

uvicorn app:app --reload


Open Streamlit UI:

streamlit run streamlit_app.py


Start a conversation and send messages like:

"I want a spicy burger under $10"


Use search tab to filter products by category or price.

Use admin panel to add new products (token: letmein).

Notes

Products use placeholder images from picsum.photos.

Interest scoring is rule-based (simple heuristics).

This project is a prototype for internship assessment and demo purposes.

Workflow Diagram (ASCII)
User
  │
  ▼
Streamlit UI ───► FastAPI Backend ──► SQLite DB
  │                  │
  │                  └──► Products Table
  │                  └──► Conversations & Messages
  ▼
Bot Response
