#!/usr/bin/env python3

import argparse
import os
import struct
import sys

# geteltorito.py: a bootimage extractor
# Script that will extract the first El Torito bootimage from a
# bootable CD image
# R. Krienke 08/2001
# krienke@uni-koblenz.de
# License: GPL V3

UTIL_VERSION = "0.6"

V_SEC_SIZE = 512
SEC_SIZE = 2048


def get_sector(file, sec_num, sec_count):
    """
    Read a particular sector from a file
    sector counting starts at 0, not 1
    """
    try:
        file.seek(sec_num * SEC_SIZE)
        return file.read(V_SEC_SIZE * sec_count)
    except IOError as ex:
        print(f"Error reading from file: {ex}", file=sys.stderr)
        return None


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Extract an El Torito image from a bootable CD (or cd-image).",
        add_help=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"Version: {UTIL_VERSION}"
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_filename",
        help="Write extracted data to file <file> instead of STDOUT.",
    )
    parser.add_argument("image_file", help="CD image file or device.")

    args = parser.parse_args()

    image_file_path = args.image_file

    if not os.access(image_file_path, os.R_OK):
        print(
            f'Cannot read image/device "{image_file_path}". Aborting', file=sys.stderr
        )
        sys.exit(1)

    try:
        with open(image_file_path, "rb") as image_file:
            # Read Sector 17
            sector = get_sector(image_file, 17, 1)
            if not sector:
                sys.exit(1)

            boot, iso_ident, version, torito_spec, _, boot_p = struct.unpack(
                "<B5sB32s32sI", sector[:75]
            )

            iso_ident = iso_ident.decode("ascii")
            torito_spec = torito_spec.strip(b"\0").decode("ascii")

            if iso_ident != "CD001" or torito_spec != "EL TORITO SPECIFICATION":
                print(
                    "This data image does not seem to be a bootable CD-image",
                    file=sys.stderr,
                )
                sys.exit(1)

            # Fetch the booting catalog sector
            sector = get_sector(image_file, boot_p, 1)
            if not sector:
                sys.exit(1)

            print(f"Booting catalog starts at sector: {boot_p}", file=sys.stderr)

            # Validation Entry
            validate_entry = sector[:32]
            header, platform, _, manufact, _, five, aa = struct.unpack(
                "<BBH24sHBB", validate_entry
            )

            if header != 1 or five != 0x55 or aa != 0xAA:
                print("Invalid Validation Entry on image", file=sys.stderr)
                sys.exit(1)

            print(
                f"Manufacturer of CD: {manufact.strip(b'\\0').decode('ascii', 'ignore')}",
                file=sys.stderr,
            )
            print("Image architecture: ", end="", file=sys.stderr)
            if platform == 0:
                print("x86", file=sys.stderr)
            elif platform == 1:
                print("PowerPC", file=sys.stderr)
            elif platform == 2:
                print("Mac", file=sys.stderr)
            else:
                print(f"unknown ({platform})", file=sys.stderr)

            # Initial/Default Entry
            initial_entry = sector[32:64]
            boot, media, load_segment, system_type, _, s_count, img_start, _ = (
                struct.unpack("<BBHBBH_I_B", initial_entry)
            )

            if boot != 0x88:
                print(
                    "Boot indicator in Initial/Default-Entry is not 0x88. CD is not bootable.",
                    file=sys.stderr,
                )
                sys.exit(1)

            print("Boot media type is: ", end="", file=sys.stderr)
            count = 0
            if media == 0:
                print("no emulation", file=sys.stderr)
            elif media == 1:
                print("1.2meg floppy", file=sys.stderr)
                count = 1200 * 1024 // V_SEC_SIZE
            elif media == 2:
                print("1.44meg floppy", file=sys.stderr)
                count = 1440 * 1024 // V_SEC_SIZE
            elif media == 3:
                print("2.88meg floppy", file=sys.stderr)
                count = 2880 * 1024 // V_SEC_SIZE
            elif media == 4:
                print("harddisk", file=sys.stderr)
                mbr = get_sector(image_file, img_start, 1)
                if mbr:
                    partition1 = mbr[446:462]
                    _, first_sector, partition_size = struct.unpack("<8sII", partition1)
                    count = first_sector + partition_size

            cnt = s_count if count == 0 else count

            print(
                f"El Torito image starts at sector {img_start} and has {cnt} sector(s) of {V_SEC_SIZE} Bytes",
                file=sys.stderr,
            )

            # Read the boot image
            image = get_sector(image_file, img_start, cnt)

            if image:
                if args.output_filename:
                    try:
                        with open(args.output_filename, "wb") as out_file:
                            out_file.write(image)
                        print(
                            f'\nImage has been written to file "{args.output_filename}".',
                            file=sys.stderr,
                        )
                    except IOError as ex:
                        print(
                            f'Cannot open outputfile "{args.output_filename}" for writing. Stop. Error: {ex}',
                            file=sys.stderr,
                        )
                        sys.exit(1)
                else:
                    sys.stdout.buffer.write(image)
                    print("Image has been written to stdout ....", file=sys.stderr)

    except FileNotFoundError as _fnfe:
        print(f'Image file not found: "{image_file_path}"', file=sys.stderr)
        sys.exit(1)
    except Exception as ex:
        print(f"An error occurred: {ex}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
