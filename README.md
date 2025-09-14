# FoodieBot — Fast-Food Recommendation & Chat System

## Project Overview
FoodieBot is an interactive system that allows users to chat with a recommendation bot, search products, and view personalized suggestions based on preferences, dietary restrictions, budget, and mood. It also provides an admin panel and basic analytics.

**Features:**
- Live chat with FoodieBot
- Product search and filtering
- Interest scoring of user messages
- Admin panel to create products
- Analytics: top products, total conversations, messages

---

## Project Structure
FoodieBot/
├─ generate_products.py # Generates 100 sample fast-food products into products.json
├─ db_setup.py # Creates SQLite DB (products.db) and populates products table
├─ app.py # FastAPI backend with chat, search, admin, analytics endpoints
├─ streamlit_app.py # Streamlit frontend UI for chat, search, admin, analytics
├─ products.json # Generated sample product data
├─ products.db # SQLite database created by db_setup.py
└─ requirements.txt # Python dependencies

---

## Setup Instructions

1. **Clone the project**  
```bash
git clone <your_repo_url>
cd FoodieBot

pip install -r requirements.txt

python generate_products.py
#this creates products.json with 100 sample items.

python db_setup.py
#This creates products.db and populates the products table. It also creates tables for conversations and messages.

uvicorn app:app --reload
#The API will be available at http://localhost:8000.

streamlit run streamlit_app.py
#Open the local URL provided by Streamlit to interact with the UI.

How It Works
1. Chat System

Users start a conversation via the sidebar.

Messages are sent to the FastAPI backend.

Signals are extracted from user text (preferences, mood, budget, dietary restrictions).

Interest score is computed and products are ranked based on match.

Bot responds with top 6 product suggestions and interest score.

2. Search / Filter

Search by name/description

Filter by category and max price

Results include popularity score and relevance

3. Admin Panel

Token-protected (default token: letmein)

Create new products with basic details

4. Analytics

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

FastAPI backend with endpoints:

/conversation — start conversation

/conversation/{id}/message — send message and get product matches

/search — search products

/admin/product — create product (token required)

/analytics — basic stats

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


Start a conversation, send messages like:

"I want a spicy burger under $10"


Bot responds with top product suggestions and interest score.

Use search tab to filter products by category or price.

Use admin panel to add new products (token: letmein).

Notes

Products use placeholder images from picsum.photos.

Interest scoring is rule-based (simple heuristics).

This project is a prototype for internship assessment and demo purposes.


---

If you want, I can also make a **nice small diagram workflow** in ASCII or image form that you can directly add into this README to make it more professional for submission.  

Do you want me to do that?
