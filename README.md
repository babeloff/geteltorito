# geteltorito

The new homepage since 01/06/2024 is:
<https://github.com/rainer042/geteltorito/>

An access to the old home
<https://userpages.uni-koblenz.de/~krienke/ftp/noarch/geteltorito/geteltorito.pl>
will either redirect automatically to the new github repos
or fail due to recently applied access limitations of the previous site.
From the end of 2024 the old site will no longer be accessible at all.

- **Author:** Rainer Krienke
- **Email:** krienke@uni-koblenz.de
- **License:** GPL V3
- **Version:** 0.6
- **Description:** An El Torito boot image extractor

## Usage

```
geteltorito CD-image > toritoimagefile
```

**Examples:**

```bash
geteltorito /dev/sr0 > /tmp/bootimage
```

```
geteltorito.pl foo.iso > /tmp/bootimage
```

```
geteltorito.py --input foo.iso --output /tmp/bootimage
```

```
geteltorito foo.iso > /tmp/bootimage
```

## Description

For information on El Torito see http://en.wikipedia.org/wiki/El_torito

The script will extract the initial/default boot image from a CD if it exists.
It will not extract any of other possibly existing boot images that are allowed by the El Torito standard.

The image data is written to STDOUT,
all other information is written to STDERR (e.g. type and size of image).

If you want to write the image to a file instead of STDOUT
you can specify the filename wanted on the commandline using option `-o <filename>`.
On a unix/linux system you can use shell redirection to a file (`geteltorito.pl > myFile`).

Rainer Krienke
krienke@uni-koblenz.de
