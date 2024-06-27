import streamlit as st
from color import color_palette, ColorPalette
from PIL import Image
import numpy as np
from resources import available_color_names, named_colors
from streamlit_drawable_canvas import st_canvas
import matplotlib.pyplot as plt
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
Then, use the color picker to choose your desired color from a reference image, and click 'Submit' to find the closest matching color in your palette and the recipe to mix the color with your available colors.
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
    st.markdown(
        """
        <style>
        .scrollable-container {
            height: 400px;
            overflow-y: scroll;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.write("### Color Palette Visualization")
    with st.container():
        st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
        st.image(
            st.session_state["palette_image"],
            caption="Color Palette",
            use_column_width=True,
            clamp=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

if st.session_state["palette_submitted"]:
    st.write("###")
    st.write("## Upload an image and pick a color from it:")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img_array = np.array(image)

        st.write("###")
        st.write("## Select an area to zoom in:")

        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)",
            stroke_width=3,
            stroke_color="#FF0000",
            background_image=image,
            update_streamlit=True,
            height=300,
            width=image.size[0],
            drawing_mode="rect",
            key="select_area",
        )

        if (
            canvas_result.json_data is not None
            and len(canvas_result.json_data["objects"]) > 0
        ):
            rect = canvas_result.json_data["objects"][-1]
            x1 = int(rect["left"])
            y1 = int(rect["top"])
            width = int(rect["width"])
            height = int(rect["height"])
            x2 = x1 + width
            y2 = y1 + height

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            x1 = max(0, center_x - 12)
            y1 = max(0, center_y - 12)
            x2 = min(img_array.shape[1], center_x + 13)
            y2 = min(img_array.shape[0], center_y + 13)

            zoomed_image = Image.fromarray(img_array[y1:y2, x1:x2])
            detailed_zoom_factor = 8
            zoomed_image_large = zoomed_image.resize(
                (
                    zoomed_image.size[0] * detailed_zoom_factor,
                    zoomed_image.size[1] * detailed_zoom_factor,
                ),
                Image.NEAREST,
            )
            st.session_state["zoomed_image_large"] = zoomed_image_large

            st.write("###")
            st.write("## Pick a color from the zoomed image:")
            zoomed_canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.6)",
                stroke_width=0,
                background_image=st.session_state["zoomed_image_large"],
                update_streamlit=True,
                height=zoomed_image_large.size[1],
                width=zoomed_image_large.size[0],
                drawing_mode="point",
                key="zoomed_canvas",
            )

            if zoomed_canvas_result.json_data is not None:
                if zoomed_canvas_result.json_data["objects"]:
                    dot = zoomed_canvas_result.json_data["objects"][-1]

                    zx = int(dot["left"])
                    zy = int(dot["top"])
                    zoomed_img_array = np.array(st.session_state["zoomed_image_large"])
                    if (
                        0 <= zx < zoomed_img_array.shape[1]
                        and 0 <= zy < zoomed_img_array.shape[0]
                    ):
                        picked_color = zoomed_img_array[zy, zx]
                        rgb_tuple = tuple(picked_color)
                        st.write(f"Picked color from zoomed image: RGB{rgb_tuple}")

                        st.write("###")
                        st.write("**Picked Color from Zoomed Image:**")
                        color_hex = (
                            f"#{rgb_tuple[0]:02x}{rgb_tuple[1]:02x}{rgb_tuple[2]:02x}"
                        )
                        st.markdown(
                            f"<div style='display: flex; align-items: center;'>"
                            f"<div style='width: 50px; height: 50px; background-color: {color_hex}; margin-right: 10px;'></div>"
                            f"RGB: {rgb_tuple}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

    if st.button("Submit Color"):
        if "rgb_tuple" in locals():
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
