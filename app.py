import json
import pandas as pd
import streamlit as st

HISTORY_FILE = "history.json"


def load_history():
    try:
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_history(history):
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=2)


with open("recipes.json", "r") as file:
    recipes = json.load(file)

df = pd.DataFrame(recipes)


def as_list(value):
    if isinstance(value, list):
        return value
    return [value]


for col in ["category", "protein", "side"]:
    df[col] = df[col].apply(as_list)

history = load_history()

all_categories = sorted({
    category
    for categories in df["category"]
    for category in categories
})

all_proteins = sorted({
    protein
    for proteins in df["protein"]
    for protein in proteins
})

all_sides = sorted({
    side
    for sides in df["side"]
    for side in sides
})

st.title("🍳 What Should I Cook Today?")

col1, col2 = st.columns(2)

with col1:
    selected_category = st.selectbox(
        "Choose category",
        all_categories
    )

with col2:
    selected_protein = st.selectbox(
        "Choose protein",
        ["any"] + all_proteins
    )

selected_side = st.selectbox(
    "Choose side",
    ["any"] + all_sides
)

filtered = df[
    df["category"].apply(lambda x: selected_category in x)
]

if selected_protein != "any":
    filtered = filtered[
        filtered["protein"].apply(lambda x: selected_protein in x)
    ]

if selected_side != "any":
    filtered = filtered[
        filtered["side"].apply(lambda x: selected_side in x)
    ]

avoid_recent = st.checkbox("Avoid recently cooked dishes", value=True)

if avoid_recent:
    filtered = filtered[
        ~filtered["name"].isin(history)
    ]

st.write(f"Found {len(filtered)} matching recipes.")

if st.checkbox("Show matching recipes"):
    st.dataframe(
        filtered[["name", "category", "protein", "side"]],
        use_container_width=True
    )

if st.button("🎲 Pick Random Dish"):
    if len(filtered) == 0:
        st.error("No recipes found. Maybe clear your history?")
    else:
        random_recipe = filtered.sample(1).iloc[0]

        st.markdown("## 🍽️ Tonight's Dish")
        st.success(f"### {random_recipe['name']}")

        result_col1, result_col2, result_col3 = st.columns(3)

        with result_col1:
            st.metric("Category", ", ".join(random_recipe["category"]))

        with result_col2:
            st.metric("Protein", ", ".join(random_recipe["protein"]))

        with result_col3:
            st.metric("Side", ", ".join(random_recipe["side"]))

        if random_recipe["name"] not in history:
            history.append(random_recipe["name"])
            save_history(history)

small_col1, small_col2, small_col3 = st.columns([1, 1, 5])

with small_col1:
    if st.button("🗑️ Clear History"):
        save_history([])
        st.success("History cleared.")
        st.rerun()