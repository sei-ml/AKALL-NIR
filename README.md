# AKALL NIR Project

## Overview
This project provides a set of image processing tools for analyzing RGB and Near-Infrared (NIR) data captured with depth cameras. The analyses involve extracting and processing different color channels from RGB images and NIR images for further reflectance analysis.

- The `convert` command below is part of ImageMagick, a powerful tool for image manipulation. Make sure you have it installed before running the commands.
```bash
sudo apt-get install imagemagick
```

## RGB + NIR Analysis Commands
The following commands use ImageMagick to separate the different color channels from an RGB image and process the NIR image.

### Extracting RGB Channels
At first, extract the Bluen (450nm), Green (550nm), and Red (650nm) channels from an RGB image and perform an auto-level adjustment, use the following commands:

```bash
convert RGB.jpeg -colorspace RGB -channel B -separate -auto-level B.jpeg
convert RGB.jpeg -colorspace RGB -channel G -separate -auto-level G.jpeg
convert RGB.jpeg -colorspace RGB -channel R -separate -auto-level R.jpeg
```

### Processing NIR Image
To process the NIR (850nm) image, convert the raw data into a PGM format and normalize the image:

```bash
convert -size 640x576 -depth 16 -endian LSB -define quantum:format=unsigned -define quantum:separate -depth 16 gray:NIR.raw -normalize NIR.pgm
```


