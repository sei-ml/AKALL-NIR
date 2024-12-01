import cv2
import numpy as np
import argparse
import json
import csv
from datetime import datetime

circles = []
preview_circle = None
show_magnifying_glass = False  # Initial state for magnifying tool

channel_colors = {
    "B": (255, 0, 0),  # Blue
    "G": (0, 255, 0),  # Green
    "R": (0, 0, 255),  # Red
    "NIR": (128, 128, 128)  # Gray
}

def draw_circle(event, x, y, flags, param):
    global circles, preview_circle
    channel = param
    if event == cv2.EVENT_MOUSEMOVE:
        preview_circle = (x, y)
    elif event == cv2.EVENT_LBUTTONDOWN:
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

def add_magnifying_glass(image, position, zoom_factor=2, radius=50):
    x, y = position
    height, width = image.shape[:2]

    # Get the zoomed region
    x1 = max(0, x - radius)
    y1 = max(0, y - radius)
    x2 = min(width, x + radius)
    y2 = min(height, y + radius)

    cropped = image[y1:y2, x1:x2]

    # Scale the cropped region
    zoomed = cv2.resize(cropped, None, fx=zoom_factor, fy=zoom_factor, interpolation=cv2.INTER_LINEAR)

    # Overlay the zoomed region
    overlay_x = min(width - zoomed.shape[1], x)
    overlay_y = min(height - zoomed.shape[0], y)
    image[overlay_y:overlay_y + zoomed.shape[0], overlay_x:overlay_x + zoomed.shape[1]] = zoomed

    return image

def main():
    global show_magnifying_glass

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

    csv_data = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'reflectance_data_{timestamp}.csv'

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

        # Convert grayscale to BGR for colored display
        display_image = cv2.cvtColor(resized_image, cv2.COLOR_GRAY2BGR)

        clone = display_image.copy()
        cv2.namedWindow(f"Select Circles - {channel}")
        cv2.setMouseCallback(f"Select Circles - {channel}", draw_circle, param=channel)

        print("Step 1: Click to encircle the calibration target.")
        print(f"Step 2: Click to encircle the {args.points} sample regions after the calibration target.")
        print("Press 'q' to quit. Press 'f' to toggle magnifying glass.")

        while True:
            vis_image = clone.copy()
            # Draw the permanent circles
            for circle in circles:
                color = channel_colors[channel]
                cv2.circle(vis_image, circle, 15, color, 2)
            # Draw the preview circle and magnifying glass if enabled
            if preview_circle:
                color = channel_colors[channel]
                cv2.circle(vis_image, preview_circle, 15, color, 1)

                if show_magnifying_glass:
                    vis_image = add_magnifying_glass(vis_image, preview_circle)

            cv2.imshow(f"Select Circles - {channel}", vis_image)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('f'):
                show_magnifying_glass = not show_magnifying_glass

        cv2.destroyAllWindows()

        if len(circles) < (args.points + 1):
            print(f"Error: At least one calibration target and {args.points} sample circles are required for channel {channel}.")
            circles.clear()
            continue

        calibration_center = circles[0]
        radius = 11 
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

        for i, reflection in enumerate(reflection_percentages, start=1):
            csv_data.append([channel, f"Sample {i}", reflection])

        circles.clear()

    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Channel", "Sample", "Reflectance (%)"])
        csv_writer.writerows(csv_data)

    print(f"Reflectance data saved to {csv_filename}")

if __name__ == "__main__":
    main()
