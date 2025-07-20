import streamlit as st

# ------------- Data and constants -------------

GENERATIONS = ["5", "5.5", "6", "7"]

FACEPLATE_COLORS = {
    "5_5.5": ["black", "white", "blue", "yellow", "red", "transparent"],
    "6_7": ["silver", "black", "space grey", "blue", "gold", "green", "red"],
}

CLICKWHEEL_COLORS = FACEPLATE_COLORS.copy()

CONDITIONS = ["new", "used"]

if "inventory" not in st.session_state:
    st.session_state.inventory = {
        "faceplates": {"5_5.5": {"new": {}, "used": {}}, "6_7": {"new": {}, "used": {}}},
        "clickwheels": {"5_5.5": {"new": {}, "used": {}}, "6_7": {"new": {}, "used": {}}},
    }

# -------- Helper functions ---------

def add_to_inventory(part, key, qty, generation=None, condition=None):
    inv = st.session_state.inventory
    gen_key = "5_5.5" if generation in ["5", "5.5"] else "6_7"
    if key in inv[part][gen_key][condition]:
        inv[part][gen_key][condition][key] += qty
    else:
        inv[part][gen_key][condition][key] = qty

def print_inventory_table():
    st.write("### Current Inventory")
    inv = st.session_state.inventory

    for part in ["faceplates", "clickwheels"]:
        st.write(f"**{part.capitalize()}:**")
        for gen in ["5_5.5", "6_7"]:
            st.write(f"- Gen: {gen}")
            for cond in CONDITIONS:
                st.write(f"  - Condition: {cond}")
                data = inv[part][gen][cond]
                if not data:
                    st.write("    (none)")
                else:
                    for k, v in data.items():
                        if v > 0:
                            st.write(f"    - {k}: {v}")

# --------- UI -----------

st.title("iPod Classic Faceplate & Clickwheel Configurator")

menu = st.sidebar.selectbox("Choose action", ["Add Stock", "View Inventory", "Configure iPod"])

if menu == "Add Stock":
    st.header("Add Stock")

    part = st.selectbox("Select part to add stock", ["faceplates", "clickwheels"])

    generation = st.selectbox("Generation", ["5", "5.5", "6", "7"])
    gen_key = "5_5.5" if generation in ["5", "5.5"] else "6_7"
    condition = st.selectbox("Condition", CONDITIONS)

    colors = FACEPLATE_COLORS[gen_key] if part == "faceplates" else CLICKWHEEL_COLORS[gen_key]
    color = st.selectbox("Color", colors)

    qty = st.number_input("Quantity to add", min_value=1, value=1)

    if st.button("Add to stock"):
        add_to_inventory(part, color, qty, generation=generation, condition=condition)
        st.success(f"Added {qty} {condition} {color} {part} for gen {generation} to stock.")

elif menu == "View Inventory":
    st.header("Current Inventory")
    print_inventory_table()

elif menu == "Configure iPod":
    st.header("Configure your iPod Classic")

    inv = st.session_state.inventory

    generation = st.selectbox("Choose iPod generation", GENERATIONS)
    gen_key = "5_5.5" if generation in ["5", "5.5"] else "6_7"

    condition_fp = st.selectbox("Faceplate condition", CONDITIONS)
    available_faceplates = [
        color for color, qty in inv["faceplates"][gen_key][condition_fp].items() if qty > 0
    ]
    if not available_faceplates:
        st.warning("No faceplates available for this generation and condition.")
    else:
        faceplate = st.selectbox("Faceplate color", available_faceplates)

    condition_cw = st.selectbox("Clickwheel condition", CONDITIONS)
    available_clickwheels = [
        color for color, qty in inv["clickwheels"][gen_key][condition_cw].items() if qty > 0
    ]
    if not available_clickwheels:
        st.warning("No clickwheels available for this generation and condition.")
    else:
        clickwheel = st.selectbox("Clickwheel color", available_clickwheels)

    if st.button("Check and Confirm Build"):
        errors = []

        def check_stock(part, key, gen=None, cond=None):
            inv = st.session_state.inventory
            gen_key = "5_5.5" if gen in ["5", "5.5"] else "6_7"
            return inv[part][gen_key][cond].get(key, 0) > 0

        parts_to_check = [
            ("faceplates", faceplate, generation, condition_fp),
            ("clickwheels", clickwheel, generation, condition_cw),
        ]

        for part, key, gen, cond in parts_to_check:
            if not check_stock(part, key, gen, cond):
                errors.append(f"Out of stock: {part} - {key}")

        if errors:
            st.error("Build not possible due to:")
            for e in errors:
                st.write(f"- {e}")
        else:
            st.success("Build confirmed! All parts are available.")
            for part, key, gen, cond in parts_to_check:
                gen_key = "5_5.5" if gen in ["5", "5.5"] else "6_7"
                st.session_state.inventory[part][gen_key][cond][key] -= 1
