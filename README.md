# Fix extraneous bytes before marker

I've tens of thousands digital photographs, earliest are from year 1999.
I've modified these photos with various applications over years
and some of those applications has corrupted many photos
during these modifications.

The biggest problem is this:

```
$ identify broken_orig.jpg
broken_orig.jpg JPEG 2048x1536 2048x1536+0+0 8-bit sRGB 2.03195MiB 0.000u 0:00.002
identify: Corrupt JPEG data: 2 extraneous bytes before marker 0xdb `broken_orig.jpg' @ warning/jpeg.c/JPEGWarningHandler/399.
```

The original error message originates from [libjpeg](https://www.ijg.org)
library.

This corrupted part of EXIF header prevents importing photos into
Mac Os X Photos.app and and opening in many other 
applications (including Mac Preview). 


My goal in this project is to finally fix corrupted JPEG data.

So far the best candidate to remove extraneous bytes is this Python script:
[fix-extraneous-bytes-before-marker-0xd9.py](https://gist.github.com/zwn/5d4e7cdef308d6a8eb8e5f4da19523d7)

Unfortunaltely it didn't work at all in my environment (Python 3.7) and anyway
it fixes only extraneous bytes before marker 0xd9, so I decided to modify
it a bit  

[fix-extraneous-bytes-before-marker-0xxx.py](fix-extraneous-bytes-before-marker-0xxx.py)

# Other goals

In addition I want to inject GPS location coordinates into EXIF header.
I've a good GPS track log coverage for the photos and
[exiftool](https://owl.phy.queensu.ca/~phil/exiftool/) 
can use e.g. GPX files to GPS tag photos.

# Work flow

## Convert OziExplorer track log to GPX
Not in use but here as a reminder.

`gpsbabel -i ozi -f path/to/ozi-track-file.plt -o gpx -F path/to/gpx-file.gpx`

Convert multiple files
```
for i in $(find tracks/ -name "*plt" ); do 
    echo gpsbabel -i ozi -f $i -o gpx -F $(basename -s .plt $i).gpx;
done
```

## Convert and merge lots of Ozi .plt files into one GPX file
These files start with string `20`, e.g. `2005-05-01.plt.
```
gpsbabel -i ozi -f \
  $(echo tracks/2005/*/*.plt|perl -pe 's| tracks/| -f tracks/|g') \
  -o gpx -F 2005-ozi.gpx
```

## Fix extraneous bytes before marker
```
for i in path/to/*.jpg; do 
    python fix-extraneous-bytes-before-marker-0xxx.py $i;
done
```

## Geotag a photo
`exiftool -geotag path/to/gpx-file.gpx path/to/photo.jpg`

## Set file timestamp to photo shooting time
`exiftool '-FileModifyDate<DateTimeOriginal' path/to/photo.jpg`
