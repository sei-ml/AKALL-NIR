import pandas as pd
import json
import argparse
import matplotlib.pyplot as plt

def load_data(data_file, meta_file):
    data = pd.read_csv(data_file)

    with open(meta_file, "r") as f:
        calibration = json.load(f)
    
    return data, calibration

def sanitize_color(color):
    return color.split("(")[-1].strip(")").lower()

def plot_data(data, calibration):
    """Plot the reflectance data."""
    # Extract sample metadata
    sample_metadata = calibration.get("samples", {})

    # Prepare colors and styles for plotting
    custom_styles = {
        sample_metadata[sample]["name"]: {
            "color": sample_metadata[sample]["color"],
            "linestyle": sample_metadata[sample]["linestyle"]
        }
        for sample in sample_metadata
    }

    # Extract unique channels and wavelengths
    wavelengths = [450, 550, 650, 850]  # Corresponding to B, G, R, NIR

    # Group by sample names for plotting
    grouped = data.groupby("Sample")

    # Plotting the data
    plt.figure(figsize=(12, 8))

    for sample, group in grouped:
        if sample not in sample_metadata:
            print(f"Warning: Metadata for {sample} not found. Skipping...")
            continue

        sample_name = sample_metadata[sample]["name"]
        style = custom_styles.get(sample_name, {"color": "blue", "linestyle": "-"})
        plt.plot(
            wavelengths,
            group["Reflectance (%)"].values,
            marker='o',
            color=style["color"],
            linestyle=style["linestyle"],
            label=sample_name
        )
        # Annotate the last point of each sample's data
        plt.text(
            wavelengths[-1],
            group["Reflectance (%)"].iloc[-1],
            sample_name,
            fontsize=8,
            color=style["color"],
            ha="left",
            va="center"
        )

    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Reflectance (%)")
    plt.xticks(wavelengths)
    plt.grid(True)
    plt.legend(title="Samples", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Plot reflectance data.")
    parser.add_argument("data_file", type=str, help="Path to the CSV data file.")
    parser.add_argument("--meta", type=str, required=True, help="Path to the calibration JSON file.")
    
    args = parser.parse_args()
    
    try:
        data, calibration = load_data(args.data_file, args.meta)
        
        plot_data(data, calibration)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
