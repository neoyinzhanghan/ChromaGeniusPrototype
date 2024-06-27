import mixbox

# named_colors = {
#     "Cadmium Yellow": (254, 236, 0),
#     "Hansa Yellow": (252, 211, 0),
#     "Cadmium Orange": (255, 105, 0),
#     "Cadmium Red": (255, 39, 2),
#     "Quinacridone Magenta": (128, 2, 46),
#     "Cobalt Violet": (78, 0, 66),
#     "Ultramarine Blue": (25, 0, 89),
#     "Cobalt Blue": (0, 71, 171),
#     "Phthalo Blue": (13, 27, 68),
#     "Phthalo Green": (0, 60, 50),
#     "Sap Green": (107, 148, 4),
#     "Burnt Sienna": (123, 72, 0),
# }  # TODO add more colors

named_colors = {
    # yellows
    "Cadmium Yellow Medium": (252, 234, 2),
    "Cadmium Yellow Light": (253, 218, 13),
    "Yellow Ochre": (203, 157, 6),
    "Naples Yellow": (250, 218, 94),
    "Lemon Yellow": (254, 242, 80),
    # reds
    "Scarlet Red": (255, 36, 0),
    "Alizarin Crimson": (227, 38, 54),
    "Cadmium Orange": (242, 140, 40),
    "Cadmium Red Light": (196, 27, 22),
    "Crimson Red": (178, 34, 34),
    # blues
    "Ultramarine Blue": (4, 55, 242),
    "Cerulean Blue": (42, 82, 190),
    "Light Blue Permanent": (173, 216, 230),
    "Cobalt Blue": (0, 71, 171), # GOOD
    "Phthalo Blue": (0, 15, 137), # NEED TO TEST
    # greens
    "Phthalo Green": (0, 60, 50), # GOOD
    "Pale Green": (152, 251, 152),
    "Chromium Oxide Green": (58, 139, 60),
    # black/white/brown
    "Mars Black": (22, 22, 23),
    "Titanium White": (255, 255, 255),
    "Burnt Sienna": (233, 116, 81),
    "Burnt Umber": (138, 51, 36),
    "Raw Sienna": (214, 138, 89),
    "Ivory Black": (12, 11, 10),
}

available_color_names = list(named_colors.keys())

color_groupings = {
    "yellow": [
        "Cadmium Yellow Medium",
        "Cadmium Yellow Light",
        "Yellow Ochre",
        "Naples Yellow",
        "Lemon Yellow",
    ],
    "blue": [
        "Ultramarine Blue",
        "Cerulean Blue",
        "Light Blue Permanent",
        "Cobalt Blue",
        # "Phthalo Blue",
    ],
    "red": [
        "Scarlet Red",
        "Alizarin Crimson",
        "Cadmium Orange",
        "Cadmium Red Light",
        "Crimson Red",
    ],
    "green": [
        "Phthalo Green",
        "Pale Green",
        "Chromium Oxide Green",
    ],
    "black/white/brown": [
        "Mars Black",
        "Titanium White",
        "Burnt Sienna",
        "Burnt Umber",
        "Raw Sienna",
        "Ivory Black",
    ],
}

# color1 = (0, 15, 137) # cobalt blue
# color2 = (0, 60, 50) # phthalo green

# z1 = mixbox.rgb_to_latent(color1)
# z2 = mixbox.rgb_to_latent(color2)

# z_mix = [0] * mixbox.LATENT_SIZE

# for i in range(len(z_mix)):  # mix together:
#     z_mix[i] = 0.5 * z1[i] + 0.5 * z2[i]  #   30% of rgb1

# rgb_mix = mixbox.latent_to_rgb(z_mix)
# print(rgb_mix)
