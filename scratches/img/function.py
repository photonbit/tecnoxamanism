import cv2
import svgwrite
import numpy as np

def img_to_svg(input_image, output_svg, edge_threshold1=100, edge_threshold2=200, min_line_length=100, max_line_gap=10, min_radius=3, max_radius=10):
    # Read the image
    img = cv2.imread(input_image, cv2.IMREAD_GRAYSCALE)

    # Apply Gaussian blur to reduce noise
    img = cv2.GaussianBlur(img, (5, 5), 0)

    # Perform Canny edge detection
    edges = cv2.Canny(img, edge_threshold1, edge_threshold2)

    # Initialize the SVG canvas
    height, width = img.shape
    dwg = svgwrite.Drawing(output_svg, profile='tiny', size=(width, height))

    # Hough Line Transform for detecting straight lines (axes)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=min_line_length, maxLineGap=max_line_gap)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke='black'))

    # Hough Circle Transform for detecting circles (points)
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 20, param1=edge_threshold1, param2=edge_threshold2, minRadius=min_radius, maxRadius=max_radius)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, radius = circle
            dwg.add(dwg.circle(center=(x, y), r=radius, stroke='black', fill='none'))

    # Save the SVG file
    dwg.save()

input_image = "funcion.jpg"  # Replace with the path to your image
output_svg = "output.svg"  # Replace with the path to the desired output SVG file
img_to_svg(input_image, output_svg)

