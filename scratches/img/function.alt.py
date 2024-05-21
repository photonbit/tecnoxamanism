import cv2
import os
import subprocess
import sys


def img_to_svg_potrace(input_image, output_svg, blur_size=5, threshold=128):
    # Read the image
    img = cv2.imread(input_image, cv2.IMREAD_GRAYSCALE)

    # Apply Gaussian blur to reduce noise
    img = cv2.GaussianBlur(img, (blur_size, blur_size), 0)

    # Apply threshold to create a binary image
    _, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)

    # Save the binary image as a temporary PGM file
    temp_pgm = 'temp.pgm'
    cv2.imwrite(temp_pgm, img)

    # Use potrace to convert the PGM file to an SVG
    subprocess.run(['potrace', '-s', '-o', output_svg, temp_pgm])

    # Remove the temporary PGM file
    os.remove(temp_pgm)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python img_to_svg_potrace.py <input_image> <output_svg>")
        sys.exit(1)

    input_image = sys.argv[1]
    output_svg = sys.argv[2]
    img_to_svg_potrace(input_image, output_svg, blur_size=7, threshold=100)

