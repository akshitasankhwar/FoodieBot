# streamlit_app.py
"""
Streamlit UI:
- Live chat box
- product cards with images
- real-time interest score display
- conversation history shown
- admin panel (token-based) to create products
- analytics tab showing counts and top products
"""
import streamlit as st
import requests
import time

API_BASE = "http://localhost:8000"

st.set_page_config(layout="wide", page_title="FoodieBot UI")

st.title("FoodieBot — Live Chat & Recommendations")

# Sidebar: conversation controls
st.sidebar.header("Controls")
username = st.sidebar.text_input("Your name", value="guest")
if "conv_id" not in st.session_state:
    st.session_state["conv_id"] = None
if st.session_state["conv_id"] is None:
    if st.sidebar.button("Start Conversation"):
        resp = requests.post(f"{API_BASE}/conversation", params={"user_name": username})
        conv_id = resp.json()["conversation_id"]
        st.session_state["conv_id"] = conv_id
        st.rerun()


st.sidebar.markdown("---")
tab = st.sidebar.radio("App section", ["Chat", "Search", "Admin", "Analytics"])

if tab == "Chat":
    st.subheader("Chat with FoodieBot")
    if st.session_state.get("conv_id") is None:
        st.info("Start a conversation from the sidebar.")
    else:
        conv_id = st.session_state["conv_id"]
        # display conversation history (pull messages)
        if st.button("Refresh conversation"):
            pass

        # Message input
        user_msg = st.text_input("Message:", key="user_input")
        if st.button("Send message"):
            if user_msg.strip() == "":
                st.warning("Please type a message.")
            else:
                payload = {"text": user_msg, "user_name": username}
                r = requests.post(f"{API_BASE}/conversation/{conv_id}/message", json=payload)
                data = r.json()
                # show bot response and matches
                st.markdown(f"**Bot**: {data['bot_text']}  \n**Interest score:** {data['interest_score']}%")
                matches = data["matches"]
                if matches:
                    st.markdown("### Top matches")
                    cols = st.columns(3)
                    for i, m in enumerate(matches):
                        c = cols[i % 3]
                        with c:
                            st.image(m["image_url"], width=200)
                            st.markdown(f"**{m['name']}**")
                            st.markdown(f"Category: {m['category']} • ${m['price']}")
                            st.markdown(f"Popularity: {m['popularity_score']} • Score: {m['score']}")
                            if st.button(f"Add {m['product_id']}", key=f"add_{m['product_id']}"):
                                st.success(f"Added {m['name']} to cart (demo)")

if tab == "Search":
    st.subheader("Search / Filter products")
    q = st.text_input("Search term (name/description)")
    category = st.selectbox("Category", options=[""] + ["Burgers","Pizza","Fried Chicken","Tacos & Wraps","Sides & Appetizers","Beverages","Desserts","Salads","Breakfast","Limited Time Specials"])
    max_price = st.number_input("Max price (0 = none)", value=0.0)
    if st.button("Search"):
        params = {}
        if q:
            params["q"] = q
        if category:
            params["category"] = category
        if max_price > 0:
            params["max_price"] = max_price
        resp = requests.get(f"{API_BASE}/search", params=params)
        items = resp.json()
        st.write(f"Found {len(items)} results")
        for it in items:
            st.image(it["image_url"], width=150)
            st.markdown(f"**{it['name']}** — ${it['price']} — Score: {it['score']}")

if tab == "Admin":
    st.subheader("Admin panel (token required)")
    token = st.text_input("Admin token", type="password")
    st.markdown("**Create product**")
    with st.form("create_product"):
        pid = st.text_input("product_id")
        name = st.text_input("Name")
        cat = st.text_input("Category")
        price = st.number_input("Price", value=9.99)
        img = st.text_input("Image URL", value="https://picsum.photos/seed/demo/400/300")
        submitted = st.form_submit_button("Create")
        if submitted:
            payload = {
                "product_id": pid,
                "name": name,
                "category": cat,
                "price": price,
                "ingredients": ["demo"],
                "dietary_tags": [],
                "mood_tags": [],
                "allergens": []
            }
            r = requests.post(f"{API_BASE}/admin/product", json=payload, params={"token": token})
            if r.status_code == 200:
                st.success("Created product")
            else:
                st.error(f"Failed: {r.text}")

if tab == "Analytics":
    st.subheader("Analytics")
    resp = requests.get(f"{API_BASE}/analytics")
    stats = resp.json()
    st.write(stats)
    st.markdown("Top products:")
    for t in stats.get("top_products", []):
        st.markdown(f"- {t['name']} (id: {t['product_id']}) — popularity {t['popularity_score']}")
