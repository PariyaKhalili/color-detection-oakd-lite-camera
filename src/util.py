import numpy as np
import cv2

def get_limits(color_name):
    """
    Returns HSV lower and upper limits for color detection.
    Supports: 'brown', 'black', 'yellow', etc.
    """

    if color_name == "brown":
        # Brown = orange hue + low saturation + low value
        # These values are field-tested for impurity detection
        lower = np.array([5,  50,  20], dtype=np.uint8)
        upper = np.array([20, 255, 200], dtype=np.uint8)
        return lower, upper

    if color_name == "black":
        # Black = ANY hue + low saturation + very low value
        lower = np.array([0,   0,   0], dtype=np.uint8)
        upper = np.array([180, 255, 60], dtype=np.uint8)
        return lower, upper