import cv2
import numpy as np

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
    image_path = "R_1731624458C5MJPG3072P.jpeg"
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if image is None:
        print("Error: Unable to load image. Check the file path.")
        return

    resized_image = resize_to_720p(image)

    print("Select the calibration type:")
    print("1. Blue (8.8%)")
    print("2. Green (35.6%)")
    print("3. Red (13.3%)")
    print("4. NIR (30%)")
    calibration_choice = input("Enter 1, 2, 3, or 4: ")

    calibration_reflectance = None
    if calibration_choice == "1":
        calibration_reflectance = 23.7
    elif calibration_choice == "2":
        calibration_reflectance = 25.5
    elif calibration_choice == "3":
        calibration_reflectance = 29.9
    elif calibration_choice == "4":
        calibration_reflectance = 30.0
    else:
        print("Invalid choice. Exiting.")
        return

    clone = resized_image.copy()
    cv2.namedWindow("Select Circles")
    cv2.setMouseCallback("Select Circles", draw_circle)

    print("Step 1: Click to encircle the calibration target.")
    print("Step 2: Click to encircle the 9 sample regions after the calibration target.")
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

    if len(circles) < 10:
        print("Error: At least one calibration target and 9 sample circles are required.")
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
