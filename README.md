convert 1731624458C5MJPG3072P.jpeg -colorspace RGB -channel G -separate -auto-level G_1731624458C5MJPG3072P.jpeg
convert 1731624458C5MJPG3072P.jpeg -colorspace RGB -channel B -separate -auto-level B_1731624458C5MJPG3072P.jpeg
convert 1731624458C5MJPG3072P.jpeg -colorspace RGB -channel R -separate -auto-level R_1731624458C5MJPG3072P.jpeg

convert -size 640x576 -depth 16 -endian LSB -define quantum:format=unsigned -define quantum:separate -depth 16 gray:1731624386IR5640NFOV_UNBINNED -normalize 1731624386IR5640NFOV_UNBINNED.pgm
