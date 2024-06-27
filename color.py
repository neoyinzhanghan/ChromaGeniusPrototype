import mixbox
import numpy as np
import colorspacious as cs
import matplotlib.pyplot as plt
import numpy as np
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000
from resources import named_colors, available_color_names


def patch_asscalar(a):
    return a.item()


setattr(np, "asscalar", patch_asscalar)


def rgb_to_lab(rgb):
    """
    Convert an RGB color to LAB color space.

    Args:
    rgb (tuple): A tuple of (R, G, B) values in range [0, 255].

    Returns:
    tuple: A tuple of (L*, a*, b*) values in LAB color space.
    """
    lab = cs.cspace_convert(rgb, "sRGB255", "CIELab")
    return tuple(lab)


def lab_to_rgb(lab):
    """
    Convert a LAB color to RGB color space.

    Args:
    lab (tuple): A tuple of (L*, a*, b*) values.

    Returns:
    tuple: A tuple of (R, G, B) values in range [0, 255].
    """
    rgb = cs.cspace_convert(lab, "CIELab", "sRGB255")
    return tuple(rgb)


def lab_distance(lab1, lab2):
    """
    Calculate the Delta E 2000 distance between two LAB colors.

    Args:
    lab1 (tuple): A tuple of (L*, a*, b*) values.
    lab2 (tuple): A tuple of (L*, a*, b*) values.

    Returns:
    float: The Delta E 2000 distance between the two LAB colors.
    """
    color1 = LabColor(lab_l=lab1[0], lab_a=lab1[1], lab_b=lab1[2])
    color2 = LabColor(lab_l=lab2[0], lab_a=lab2[1], lab_b=lab2[2])
    delta_e = delta_e_cie2000(color1, color2)
    return delta_e


def rgb_distance(rgb1, rgb2):
    """First convert the color to lab color space and then calculate the distance in lab color space"""
    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)
    return lab_distance(lab1, lab2)


class Color:
    """A color class. This class represents the mixing tree leading to the specified color.
    === Class Attributes ===
    - rgb: The RGB value of the color as a tuple (r, g, b)
    - parents: a list of doubles [(p, a), ...] where p is a Color object and a is the proportion of p in the mixture
        If parents is an empty list that means that the Color object is a source color
    - name: the name of the color
    """

    def __init__(self, rgb, name=None):
        """Initialize a new color with the given RGB value."""
        self.rgb = rgb
        self.parents = []
        self.name = name

    def add_parent(self, parent, proportion):
        """Add a parent to this color with the given proportion."""
        self.parents.append((parent, proportion))

    def is_source_color(self):
        """Return whether this color is a source color."""
        return len(self.parents) == 0

    def mix(self, other, proportion):
        """Mix this color with another color in the given proportion."""
        assert 0 <= proportion <= 1, "Proportion must be between 0 and 1"
        mixed_rgb = mixbox.lerp(self.rgb, other.rgb, proportion)

        new_color = Color(mixed_rgb)

        new_color.add_parent(self, proportion)
        new_color.add_parent(other, 1 - proportion)

        return new_color

    def __str__(self) -> str:
        if self.name is None:
            parents = self.parents
            recipe_str = ", ".join([f"{parent[0].name}" for parent in parents])
            return f"Mixed Color: {self.rgb}, Recipe: {recipe_str}."
        else:
            return f"{self.name}: {self.rgb}"


class ColorPalette:
    """A ColorPalette class. This class represent a tree-like color palette for a collectection of selected source colors.
    For now the level of tree is just 1 and we are interpolating between any two colors. Later we will have a better database.
    === Class Attributes ===
    - refinement_level: the number of interpolation steps between each color in the palette
    - source_colors: a list of Color objects representing the source colors
    - rgb_to_color: a dictionary mapping RGB values to Color objects
    """

    def __init__(self, source_colors_names, refinement_level=8):
        """Initialize a new color palette with the given source colors."""
        self.refinement_level = refinement_level
        self.source_colors = []
        self.rgb_to_color = {}

        # first get all the keys from named_colors
        named_colors_keys = list(named_colors.keys())

        # assert that the source colors are in named_colors
        for color_name in source_colors_names:
            assert (
                color_name in named_colors_keys
            ), f"Proposed source color named {color_name} is not in named_colors"

        for source_color_name in source_colors_names:
            source_color_rgb = named_colors[source_color_name]
            source_color = Color(rgb=source_color_rgb, name=source_color_name)
            self.source_colors.append(source_color)
            self.rgb_to_color[source_color_rgb] = source_color

        for i in range(len(self.source_colors)):
            for j in range(i + 1, len(self.source_colors)):
                color1 = self.source_colors[i]
                color2 = self.source_colors[j]
                for k in range(1, self.refinement_level):
                    proportion = k / self.refinement_level
                    new_color = color1.mix(color2, proportion)
                    self.rgb_to_color[new_color.rgb] = new_color

    def search_color(self, rgb):
        """Return the Color object with rgb value closest to the given rgb value."""

        closest_color = None
        closest_distance = float("inf")

        for color_rgb in self.rgb_to_color:
            distance = rgb_distance(color_rgb, rgb)
            if distance < closest_distance:
                closest_distance = distance
                closest_color = self.rgb_to_color[color_rgb]

        return closest_color


color_palette = ColorPalette(
    source_colors_names=available_color_names, refinement_level=10
)


def visualize_palette(color_palette, filename="color_palette.png"):
    # Extract the colors and their names from the dictionary
    colors = list(color_palette.rgb_to_color.keys())
    color_names = list(color_palette.rgb_to_color.values())

    # Determine the number of columns for the visualization
    num_colors = len(colors)
    num_cols = 10  # Set the number of columns
    num_rows = int(np.ceil(num_colors / num_cols))

    # Create a figure and axes
    fig, ax = plt.subplots(figsize=(num_cols, num_rows))

    # Hide the axes
    ax.set_axis_off()

    # Plot each color as a rectangle
    for i, color in enumerate(colors):
        row = i // num_cols
        col = i % num_cols
        color_hex = "#{:02x}{:02x}{:02x}".format(*color)

        # Draw the rectangle with the color
        rect = plt.Rectangle((col, num_rows - row - 1), 1, 1, color=color_hex)
        ax.add_patch(rect)

        # Add the color name as text
        ax.text(
            col + 0.5,
            num_rows - row - 1.5,
            color_names[i],
            ha="center",
            va="center",
            fontsize=8,
            color="black",
        )

    # Set the limits and aspect ratio
    ax.set_xlim(0, num_cols)
    ax.set_ylim(0, num_rows)
    ax.set_aspect("equal")

    # Save the plot as an image file
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


# Example usage:
visualize_palette(color_palette)
