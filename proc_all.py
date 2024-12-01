import cv2
import numpy as np
import argparse
import json

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
    parser = argparse.ArgumentParser(description="Process images for reflectance analysis.")
    parser.add_argument("--blue", type=str, required=True, help="Path to the blue channel image file.")
    parser.add_argument("--green", type=str, required=True, help="Path to the green channel image file.")
    parser.add_argument("--red", type=str, required=True, help="Path to the red channel image file.")
    parser.add_argument("--nir", type=str, required=True, help="Path to the NIR image file.")
    parser.add_argument("--points", type=int, default=9, help="Number of sample points to select.")
    parser.add_argument("--calibration", type=str, required=True, help="Path to the calibration JSON file.")
    args = parser.parse_args()

    with open(args.calibration, 'r') as file:
        calibration_data = json.load(file)

    images = {
        "B": args.blue,
        "G": args.green,
        "R": args.red,
        "NIR": args.nir
    }

    for channel, image_path in images.items():
        if channel not in calibration_data:
            print(f"Invalid channel specified: {channel}. Exiting.")
            return

        calibration_reflectance = calibration_data[channel]
        print(f"Processing channel: {channel} (Calibration reflectance: {calibration_reflectance}%)")

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        if image is None:
            print(f"Error: Unable to load image for channel {channel}. Check the file path.")
            continue

        resized_image = resize_to_720p(image)

        clone = resized_image.copy()
        cv2.namedWindow(f"Select Circles - {channel}")
        cv2.setMouseCallback(f"Select Circles - {channel}", draw_circle)

        print("Step 1: Click to encircle the calibration target.")
        print(f"Step 2: Click to encircle the {args.points} sample regions after the calibration target.")
        print("Press 'q' when done.")

        while True:
            vis_image = clone.copy()
            for circle in circles:
                cv2.circle(vis_image, circle, 10, (255), 2)
            cv2.imshow(f"Select Circles - {channel}", vis_image)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        cv2.destroyAllWindows()

        if len(circles) < (args.points + 1):
            print(f"Error: At least one calibration target and {args.points} sample circles are required for channel {channel}.")
            circles.clear()
            continue

        calibration_center = circles[0]
        radius = 10 
        calibration_intensity = get_average_intensity(resized_image, calibration_center, radius)

        print(f"Calibration Intensity for {channel}: {calibration_intensity}")
        print(f"Calibration Reflectance: {calibration_reflectance}%")

        sample_intensities = []
        for center in circles[1:]:
            intensity = get_average_intensity(resized_image, center, radius)
            sample_intensities.append(intensity)

        reflection_percentages = [
            (sample / calibration_intensity) * calibration_reflectance for sample in sample_intensities
        ]

        print(f"Reflectance percentages for each sample (relative to selected calibration) for channel {channel}:")
        for i, reflection in enumerate(reflection_percentages, start=1):
            print(f"Sample {i}: {reflection:.2f}%")

        circles.clear()

if __name__ == "__main__":
    main()