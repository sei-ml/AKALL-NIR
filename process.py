import cv2
import numpy as np
import argparse

circles = []

def draw_circle(event, x, y, flags, param):
    global circles
    if event == cv2.EVENT_LBUTTONDOWN:
        circles.append((x, y))
        print(f"Circle added at: {x}, {y}")

def get_average_intensity(image, center, radius):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    return cv2.mean(image, mask=mask)[0]

def resize_to_720p(image):
    target_height = 720
    target_width = 1280
    height, width = image.shape[:2]

    scale_factor = min(target_width / width, target_height / height)
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

def main():
    parser = argparse.ArgumentParser(description="Process an image for reflectance analysis.")
    parser.add_argument("image_path", type=str, help="Path to the image file.")
    parser.add_argument("--channel", type=str, choices=["R", "G", "B", "NIR"], required=True, help="Color channel to analyze.")
    parser.add_argument("--points", type=int, default=9, help="Number of sample points to select.")
    args = parser.parse_args()

    image = cv2.imread(args.image_path, cv2.IMREAD_GRAYSCALE)
    
    if image is None:
        print("Error: Unable to load image. Check the file path.")
        return

    resized_image = resize_to_720p(image)

    #Relative B, G, R Reflectance computed from NIR images.
    calibration_reflectance = None
    if args.channel == "B":
        calibration_reflectance = 12.21
        print("Calibration type: Blue (12.21%)")
    elif args.channel == "G":
        calibration_reflectance = 27.54
        print("Calibration type: Green (27.54%)")
    elif args.channel == "R":
        calibration_reflectance = 40.88
        print("Calibration type: Red (40.88%)")
    elif args.channel == "NIR":
        calibration_reflectance = 30.0
        print("Calibration type: NIR (30%)")
    else:
        print("Invalid channel specified. Exiting.")
        return

    clone = resized_image.copy()
    cv2.namedWindow("Select Circles")
    cv2.setMouseCallback("Select Circles", draw_circle)

    print("Step 1: Click to encircle the calibration target.")
    print(f"Step 2: Click to encircle the {args.points} sample regions after the calibration target.")
    print("Press 'q' when done.")

    while True:
        vis_image = clone.copy()
        for circle in circles:
            cv2.circle(vis_image, circle, 10, (255), 2)
        cv2.imshow("Select Circles", vis_image)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()

    if len(circles) < (args.points + 1):
        print(f"Error: At least one calibration target and {args.points} sample circles are required.")
        return

    calibration_center = circles[0]
    radius = 10 
    calibration_intensity = get_average_intensity(resized_image, calibration_center, radius)

    print(f"Calibration Intensity: {calibration_intensity}")
    print(f"Calibration Reflectance: {calibration_reflectance}%")

    sample_intensities = []
    for center in circles[1:]:
        intensity = get_average_intensity(resized_image, center, radius)
        sample_intensities.append(intensity)

    reflection_percentages = [
        (sample / calibration_intensity) * calibration_reflectance for sample in sample_intensities
    ]

    print("Reflectance percentages for each sample (relative to selected calibration):")
    for i, reflection in enumerate(reflection_percentages, start=1):
        print(f"Sample {i}: {reflection:.2f}%")

if __name__ == "__main__":
    main()