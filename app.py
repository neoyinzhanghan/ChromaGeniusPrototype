import streamlit as st
from color import color_palette, ColorPalette
from PIL import Image
import numpy as np
from resources import available_color_names, named_colors
import matplotlib.pyplot as plt
import base64
from io import BytesIO


def visualize_palette(color_palette):
    colors = list(color_palette.rgb_to_color.keys())
    num_colors = len(colors)
    num_cols = 10
    num_rows = int(np.ceil(num_colors / num_cols))

    fig, ax = plt.subplots(figsize=(num_cols, num_rows))
    ax.set_axis_off()

    for i, color in enumerate(colors):
        row = i // num_cols
        col = i % num_cols
        color_hex = "#{:02x}{:02x}{:02x}".format(*color)
        rect = plt.Rectangle((col, num_rows - row - 1), 1, 1, color=color_hex)
        ax.add_patch(rect)

    ax.set_xlim(0, num_cols)
    ax.set_ylim(0, num_rows)
    ax.set_aspect("equal")

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)

    return buf


# Streamlit app
st.title("🎨 ChromaGenius Paint Mixer")

st.write(
    """
Welcome to the Color Palette Search App! 
Select the colors you want to include in your palette from the list below. 
Then, use the color picker to choose your desired color, and click 'Submit' to find the closest matching color in your palette and the recipe to mix the color with your available colors.
"""
)

# Initialize session state
if "palette_submitted" not in st.session_state:
    st.session_state["palette_submitted"] = False

if "zoomed_image" not in st.session_state:
    st.session_state["zoomed_image"] = None

if "selected_colors" not in st.session_state:
    st.session_state["selected_colors"] = []

if "custom_colors" not in st.session_state:
    st.session_state["custom_colors"] = []

all_colors = available_color_names + st.session_state["custom_colors"]

selected_colors = st.multiselect(
    "Select available colors:",
    options=all_colors,
    default=st.session_state["selected_colors"],
    format_func=lambda name: name,
)

st.session_state["selected_colors"] = selected_colors

col1, col2 = st.columns(2)
if col1.button("Select All"):
    st.session_state["selected_colors"] = all_colors
if col2.button("Deselect All"):
    st.session_state["selected_colors"] = []

st.write("###")
st.write("**Or add custom colors to the palette:**")

custom_color_name = st.text_input("Custom Color Name:", key="custom_color_name")
custom_color_picker = st.color_picker(
    "Pick the custom color:", "#000000", key="custom_color_picker"
)

if st.button("Add Custom Color"):
    if custom_color_name and custom_color_picker:
        custom_rgb_tuple = tuple(
            int(custom_color_picker[i : i + 2], 16) for i in (1, 3, 5)
        )
        named_colors[custom_color_name] = custom_rgb_tuple
        if custom_color_name not in st.session_state["selected_colors"]:
            st.session_state["selected_colors"].append(custom_color_name)
        if custom_color_name not in st.session_state["custom_colors"]:
            st.session_state["custom_colors"].append(custom_color_name)
        st.experimental_rerun()

if st.session_state["selected_colors"]:
    st.write("###")
    st.write("**Selected Colors:**")
    for color_name in st.session_state["selected_colors"]:
        color_value = named_colors[color_name]
        color_hex = f"#{color_value[0]:02x}{color_value[1]:02x}{color_value[2]:02x}"
        st.markdown(
            f"<div style='display: flex; align-items: center;'>"
            f"<div style='width: 20px; height: 20px; background-color: {color_hex}; margin-right: 10px;'></div>"
            f"{color_name} RGB: {color_value}"
            f"</div>",
            unsafe_allow_html=True,
        )

    selected_named_colors = {
        name: named_colors[name] for name in st.session_state["selected_colors"]
    }
    color_palette_custom = ColorPalette(selected_named_colors)

    if st.button("Submit Palette"):
        st.session_state["palette_submitted"] = True
        st.session_state["palette_image"] = visualize_palette(color_palette_custom)

if st.session_state["palette_submitted"] and "palette_image" in st.session_state:
    st.write("### Color Palette Visualization")

    # Convert the image to base64
    image_bytes = st.session_state["palette_image"].getvalue()
    encoded_image = base64.b64encode(image_bytes).decode()

    # Create HTML to display the image inside the scrollable container
    html_code = f"""
    <div class="scrollable-container">
        <img src="data:image/png;base64,{encoded_image}" alt="Color Palette" style="width: 100%;">
    </div>
    <style>
    .scrollable-container {{
        height: 400px;
        width: 100%;
        overflow-y: scroll;
        border: 1px solid #ccc;
    }}
    </style>
    """
    st.markdown(html_code, unsafe_allow_html=True)

if st.session_state["palette_submitted"]:
    st.write("###")
    st.write("## Pick a color:")

    picked_color = st.color_picker("Pick a color to match from the palette:", "#ffffff")

    if st.button("Submit Color"):
        rgb_tuple = tuple(int(picked_color[i : i + 2], 16) for i in (1, 3, 5))
        user_color = color_palette_custom.search_color(rgb_tuple)
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Input Color")
            image = Image.new("RGB", (100, 100), rgb_tuple)
            st.image(image, caption=f"RGB: {rgb_tuple}")

        with col2:
            st.subheader("Matched Color")
            search_image = Image.new("RGB", (100, 100), user_color.rgb)
            st.image(search_image, caption=f"RGB: {user_color.rgb}")

        st.write("###")
        st.write(f"**Details of the matched color:**")
        st.write(f"**RGB:** {user_color.rgb}")
        st.write(f"**Color Object:** {user_color}")

    else:
        st.write("###")
        st.write(
            "Use the color picker above to choose a color and click 'Submit Color'."
        )
