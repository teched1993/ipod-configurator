import streamlit as st

# ------------- Data and constants -------------

GENERATIONS = ["5", "5.5", "6", "7"]

FACEPLATE_COLORS = {
    "5_5.5": ["black", "white", "blue", "yellow", "red", "transparent"],
    "6_7": ["silver", "black", "space grey", "blue", "gold", "green", "red"],
}

CLICKWHEEL_COLORS = FACEPLATE_COLORS.copy()
CENTRAL_BUTTON_COLORS = FACEPLATE_COLORS.copy()

BACKPLATE_SIZES = ["30", "60", "64", "80", "120", "128", "160", "256", "512", "1TB"]
BACKPLATE_ENGRAVINGS = BACKPLATE_SIZES + ["U2"]

HARD_DISK_SIZES = ["30", "60", "80", "120", "160"]
SSD_SIZES = ["64", "128", "256"]
IFLASH_SIZES = ["128", "256", "512", "1TB", "1.5TB", "2TB"]

BATTERIES = ["650", "850", "2000"]

# Allowed conditions where needed
CONDITIONS = ["new", "used"]

# --- Inventory structure ---
if "inventory" not in st.session_state:
    st.session_state.inventory = {
        "backplates": {"new": {}, "used": {}},  # key: size + _thin/_thick or U2
        "faceplates": {"5_5.5": {"new": {}, "used": {}}, "6_7": {"new": {}, "used": {}}},
        "clickwheels": {"5_5.5": {"new": {}, "used": {}}, "6_7": {"new": {}, "used": {}}},
        "central_buttons": {"5_5.5": {"new": {}, "used": {}}, "6_7": {"new": {}, "used": {}}},
        "hard_disks": {},
        "ssds": {},
        "iflash": {},
        "batteries": {},
    }


# -------- Helper functions ---------

def add_to_inventory(part, key, qty, generation=None, condition=None):
    inv = st.session_state.inventory
    if part in ["faceplates", "clickwheels", "central_buttons"]:
        gen_key = "5_5.5" if generation in ["5", "5.5"] else "6_7"
        if key in inv[part][gen_key][condition]:
            inv[part][gen_key][condition][key] += qty
        else:
            inv[part][gen_key][condition][key] = qty
    elif part == "backplates":
        # key includes size + thin/thick or U2
        if key in inv["backplates"][condition]:
            inv["backplates"][condition][key] += qty
        else:
            inv["backplates"][condition][key] = qty
    else:
        # hard_disks, ssds, iflash, batteries
        if key in inv[part]:
            inv[part][key] += qty
        else:
            inv[part][key] = qty


def print_inventory_table():
    st.write("### Current Inventory")
    inv = st.session_state.inventory

    # Backplates
    st.write("**Backplates:**")
    for cond in CONDITIONS:
        st.write(f"- Condition: {cond}")
        data = inv["backplates"][cond]
        if not data:
            st.write("  (none)")
        else:
            for k, v in data.items():
                if v > 0:
                    st.write(f"  - {k}: {v}")

    # Faceplates, clickwheels, central buttons
    for part in ["faceplates", "clickwheels", "central_buttons"]:
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

    # Hard disks, SSDs, iFlash, Batteries
    for part in ["hard_disks", "ssds", "iflash", "batteries"]:
        st.write(f"**{part.replace('_',' ').capitalize()}:**")
        data = inv[part]
        if not data:
            st.write("  (none)")
        else:
            for k, v in data.items():
                if v > 0:
                    st.write(f"  - {k}: {v}")


# --------- UI -----------

st.title("iPod Classic Parts Stock & Configurator")

menu = st.sidebar.selectbox("Choose action", ["Add Stock", "View Inventory", "Configure iPod"])

# --- Add Stock ---
if menu == "Add Stock":
    st.header("Add Stock")

    part = st.selectbox("Select part to add stock", [
        "backplates", "faceplates", "clickwheels", "central_buttons",
        "hard_disks", "ssds", "iflash", "batteries"
    ])

    # Input controls depending on part
    if part == "backplates":
        condition = st.selectbox("Condition", CONDITIONS)
        # Used backplates: only sizes 30,60,80,120,160
        allowed_sizes = BACKPLATE_SIZES if condition == "new" else ["30", "60", "80", "120", "160"]
        size = st.selectbox("Size / Engraving", allowed_sizes + (["U2"] if condition=="new" else []))
        # Thickness
        thickness = None
        if size != "U2":
            if condition == "used" and size == "60":
                # used 60 always thick
                thickness = "thick"
                st.write("Used 60GB backplates are always thick.")
            else:
                thickness = st.selectbox("Thickness", ["thin", "thick"])
        else:
            thickness = ""

        key = f"{size}_{thickness}".strip("_")

        qty = st.number_input("Quantity to add", min_value=1, value=1)

        if st.button("Add to stock"):
            add_to_inventory(part, key, qty, condition=condition)
            st.success(f"Added {qty} {condition} backplates {key} to stock.")

    elif part in ["faceplates", "clickwheels", "central_buttons"]:
        generation = st.selectbox("Generation", ["5", "5.5", "6", "7"])
        gen_key = "5_5.5" if generation in ["5", "5.5"] else "6_7"
        condition = st.selectbox("Condition", CONDITIONS)

        if part == "faceplates":
            colors = FACEPLATE_COLORS[gen_key]
        elif part == "clickwheels":
            colors = CLICKWHEEL_COLORS[gen_key]
        else:
            colors = CENTRAL_BUTTON_COLORS[gen_key]

        color = st.selectbox("Color", colors)

        qty = st.number_input("Quantity to add", min_value=1, value=1)

        if st.button("Add to stock"):
            add_to_inventory(part, color, qty, generation=generation, condition=condition)
            st.success(f"Added {qty} {condition} {color} {part} for gen {generation} to stock.")

    elif part in ["hard_disks", "ssds", "iflash"]:
        if part == "hard_disks":
            sizes = HARD_DISK_SIZES
        elif part == "ssds":
            sizes = SSD_SIZES
        else:
            sizes = IFLASH_SIZES

        size = st.selectbox("Size", sizes)
        qty = st.number_input("Quantity to add", min_value=1, value=1)

        if st.button("Add to stock"):
            add_to_inventory(part, size, qty)
            st.success(f"Added {qty} {size} {part} to stock.")

    elif part == "batteries":
        size = st.selectbox("Battery mAh", BATTERIES)
        qty = st.number_input("Quantity to add", min_value=1, value=1)

        if st.button("Add to stock"):
            add_to_inventory(part, size, qty)
            st.success(f"Added {qty} {size} mAh batteries to stock.")


# --- View Inventory ---
elif menu == "View Inventory":
    st.header("Current Inventory")
    print_inventory_table()


# --- Configurator ---
elif menu == "Configure iPod":
    st.header("Configure your iPod Classic")

    inv = st.session_state.inventory

    generation = st.selectbox("Choose iPod generation", GENERATIONS)
    gen_key = "5_5.5" if generation in ["5", "5.5"] else "6_7"

    # Faceplate
    condition_fp = st.selectbox("Faceplate condition", CONDITIONS)
    # Get available faceplates of this gen and condition that have stock >0
    available_faceplates = [
        color for color, qty in inv["faceplates"][gen_key][condition_fp].items() if qty > 0
    ]
    if not available_faceplates:
        st.warning("No faceplates available for this generation and condition.")
    else:
        faceplate = st.selectbox("Faceplate color", available_faceplates)

    # Clickwheel
    condition_cw = st.selectbox("Clickwheel condition", CONDITIONS)
    available_clickwheels = [
        color for color, qty in inv["clickwheels"][gen_key][condition_cw].items() if qty > 0
    ]
    if not available_clickwheels:
        st.warning("No clickwheels available for this generation and condition.")
    else:
        clickwheel = st.selectbox("Clickwheel color", available_clickwheels)

    # Central button
    condition_cb = st.selectbox("Central button condition", CONDITIONS)
    available_cb = [
        color for color, qty in inv["central_buttons"][gen_key][condition_cb].items() if qty > 0
    ]
    if not available_cb:
        st.warning("No central buttons available for this generation and condition.")
    else:
        central_button = st.selectbox("Central button color", available_cb)

    # Storage type selection
    storage_type = st.selectbox("Storage type", ["hard_disks", "ssds", "iflash"])

    if storage_type == "hard_disks":
        available_storage = [
            size for size, qty in inv["hard_disks"].items() if qty > 0
        ]
    elif storage_type == "ssds":
        available_storage = [
            size for size, qty in inv["ssds"].items() if qty > 0
        ]
    else:
        available_storage = [
            size for size, qty in inv["iflash"].items() if qty > 0
        ]

    if not available_storage:
        st.warning("No storage available of selected type.")
    else:
        storage_size = st.selectbox("Storage size", available_storage)

    # Backplates selection
    # Backplates are common for all gens
    condition_bp = st.selectbox("Backplate condition", CONDITIONS)
    engraving_options = list(inv["backplates"][condition_bp].keys())
    # Filter backplates by engraving matching storage size or U2 special
    filtered_backplates = []
    for bp in engraving_options:
        # key is size_thin or size_thick or U2
        # Extract size from backplate key for matching engraving with storage
        if bp == "U2" and "U2" in BACKPLATE_ENGRAVINGS:
            filtered_backplates.append(bp)
        else:
            # Split by _ to get size part
            parts = bp.split("_")
            size_part = parts[0]
            if size_part == storage_size:
                filtered_backplates.append(bp)

    if not filtered_backplates:
        st.warning("No backplates available for the storage size and condition selected.")
    else:
        backplate = st.selectbox("Backplate", filtered_backplates)

    # Battery selection depends on backplate thickness and storage type
    # Thickness from backplate key (if U2 skip)
    thickness = None
    if backplate != "U2":
        if "_" in backplate:
            thickness = backplate.split("_")[1]
        else:
            thickness = None

    # Battery options depend on thickness and storage type (rules):
    # - thick backplate: battery 650, 850, 2000 (only with ssd or iflash)
    # - thin backplate: battery 650, 2000 (only with ssd or iflash)
    # - 2000 mah only with ssd or iflash
    # if storage is hard disk -> no 2000 mah

    battery_options = []
    if thickness == "thick":
        battery_options = ["650", "850", "2000"] if storage_type in ["ssds", "iflash"] else ["650", "850"]
    elif thickness == "thin":
        battery_options = ["650", "2000"] if storage_type in ["ssds", "iflash"] else ["650"]
    else:
        battery_options = BATTERIES  # fallback

    battery = st.selectbox("Battery (mAh)", battery_options)

    # Confirm button
    if st.button("Check and Confirm Build"):
        # Validate stock availability again and stock compatibility rules
        errors = []

        # Check all chosen parts still in stock
        def check_stock(part, key, gen=None, cond=None):
            inv = st.session_state.inventory
            if part in ["faceplates", "clickwheels", "central_buttons"]:
                gen_key = "5_5.5" if gen in ["5", "5.5"] else "6_7"
                return inv[part][gen_key][cond].get(key, 0) > 0
            elif part == "backplates":
                return inv["backplates"][cond].get(key, 0) > 0
            else:
                return inv[part].get(key, 0) > 0

        parts_to_check = [
            ("faceplates", faceplate, generation, condition_fp),
            ("clickwheels", clickwheel, generation, condition_cw),
            ("central_buttons", central_button, generation, condition_cb),
            (storage_type, storage_size, None, None),
            ("backplates", backplate, None, condition_bp),
            ("batteries", battery, None, None),
        ]

        for part, key, gen, cond in parts_to_check:
            if not check_stock(part, key, gen, cond):
                errors.append(f"Out of stock: {part} - {key}")

        # Compatibility rules (as per your list):

        # 1. Used 60GB backplates always thick
        if condition_bp == "used" and backplate.startswith("60") and not backplate.endswith("thick"):
            errors.append("Used 60GB backplates must be thick.")

        # 2. Battery rules
        if battery == "2000" and storage_type == "hard_disks":
            errors.append("2000 mAh battery only with SSD or iFlash, not Hard Disk.")

        if thickness == "thick" and battery not in ["650", "850", "2000"]:
            errors.append("Invalid battery for thick backplate.")

        if thickness == "thin" and battery not in ["650", "2000"]:
            errors.append("Invalid battery for thin backplate.")

        if errors:
            st.error("Build not possible due to:")
            for e in errors:
                st.write(f"- {e}")
        else:
            st.success("Build confirmed! All parts are available and compatible.")

            # Optional: Deduct one from stock per part
            for part, key, gen, cond in parts_to_check:
                inv = st.session_state.inventory
                if part in ["faceplates", "clickwheels", "central_buttons"]:
                    gen_key = "5_5.5" if gen in ["5", "5.5"] else "6_7"
                    inv[part][gen_key][cond][key] -= 1
                elif part == "backplates":
                    inv["backplates"][cond][key] -= 1
                else:
                    inv[part][key] -= 1


