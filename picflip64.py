# -*- coding: utf-8 -*-
from typing import Tuple

# This file is part of picflip64.
# picflip64 is for converting texture files for nintendo 64
# Copyright © 2023 Gianluigi Cusimano

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from PIL import Image
import pathlib
import io
import sys
import typing


def rgba5551_decode(pixel: bytes) -> tuple[int, int, int, int]:
    color = int.from_bytes(pixel, byteorder='big')
    red = (color & 0b1111100000000000) >> (11 - 3)
    green = (color & 0b0000011111000000) >> (6 - 3)
    blue = (color & 0b0000000000111110) << 2
    alpha = color & 0b0000000000000001
    return (red, green, blue, 255 if alpha == 1 else 0)


def rgba5551_encode(red, green, blue, alpha) -> bytes:
    red = ((red & 0xff) >> 3)
    green = ((green & 0xff) >> 3)
    blue = ((blue & 0xff) >> 3)
    alpha = 1 if alpha > 128 else 0
    return ((red << 11) | (green << 6) | (blue << 1) | alpha).to_bytes(2, 'big')


def swap(data, width, height, bpp) -> bytes:
    if swap.enable == False:
        return data
    res = b''

    bytes_per_row = int(width * bpp >> 3)  # aka diviso 8
    # mi sa che inizio a leggere le colonne?
    for i in range(height):
        row = data[i * bytes_per_row:i * bytes_per_row + bytes_per_row]
        if i % 2 == 1:  # dispari
            out = b''
            if bpp == 32:
                for j in range(len(row) // 16):
                    out += row[16 * j + 8:16 * j + 16] + row[16 * j:16 * j + 8]
            else:
                for j in range(len(row) // 8):
                    out += row[8 * j + 4:8 * j + 8] + row[8 * j:8 * j + 4]
            res += out
        else:
            res += row
    return res


def decode_image_rgba32(filename: pathlib.Path, width: int, height: int) -> Image:
    """
    Convert a raw to a bmp, the format is a bit weird. Every byte contains two
    pixels, every nibble references to a palette value. Read the code, it's
    better than trying to explain.
    """
    img = Image.new('RGBA', (width, height), "black")
    pixels = img.load()

    with filename.open('rb') as raw:
        rdata = raw.read()
        swapped = swap(rdata, width, height, 32)
        data = io.BytesIO(swapped)
        data.seek(0)
        # raw_pixels = [x for x in grouper(rdata, 4, b'\x00')]
        for r in range(0, height):
            for c in range(0, width):
                pdata = data.read(4)
                pixels[c, r] = (pdata[0], pdata[1], pdata[2], pdata[3])
    return img


def decode_image_rgba16(source_path: pathlib.Path, width: int, height: int) -> Image:
    img = Image.new('RGBA', (width, height), "black")
    pixels = img.load()

    with source_path.open('rb') as raw:
        rdata = raw.read()
        swapped = swap(rdata, width, height, 16)
        data = io.BytesIO(swapped)
        data.seek(0)

        for r in range(0, height):
            for c in range(0, width):
                pdata = data.read(2)
                red, green, blue, alpha = rgba5551_decode(pdata)
                pixels[c, r] = (red & 0xff, green & 0xff, blue & 0xff, alpha)
    return img


def decode_image_i4(source_path: pathlib.Path, width: int, height: int) -> Image:
    img = Image.new('RGBA', (width, height), "black")
    pixels = img.load()

    with source_path.open('rb') as raw:
        rdata = raw.read()
        swapped = swap(rdata, int(width / 2), height, 8)
        data = io.BytesIO(swapped)
        data.seek(0)

        for r in range(0, height):
            for c in range(0, width, 2):
                raw_pixel = int.from_bytes(data.read(1), 'big')

                left_color = raw_pixel & 0b11110000
                right_color = (raw_pixel & 0b00001111) << 4

                pixels[c, r] = (left_color, left_color, left_color, 255)
                pixels[c + 1, r] = (right_color, right_color, right_color, 255)
    return img


def decode_image_i8(source_path: pathlib.Path, width: int, height: int) -> Image:
    img = Image.new('RGBA', (width, height), "black")
    pixels = img.load()

    with source_path.open('rb') as raw:
        rdata = raw.read()
        swapped = swap(rdata, width, height, 8)
        data = io.BytesIO(swapped)
        data.seek(0)

        for r in range(0, height):
            for c in range(0, width):
                raw_pixel = int.from_bytes(data.read(1), 'big')
                pixels[c, r] = (raw_pixel, raw_pixel, raw_pixel, 255)
    return img


def decode_image_ia4(source_path: pathlib.Path, width: int, height: int) -> Image:
    img = Image.new('RGBA', (width, height), "black")
    pixels = img.load()

    with source_path.open('rb') as raw:
        rdata = raw.read()
        swapped = swap(rdata, int(width / 2), height, 8)
        data = io.BytesIO(swapped)
        data.seek(0)

        for r in range(0, height):
            for c in range(0, width, 2):
                raw_pixel = int.from_bytes(data.read(1), 'big')
                left_i = (raw_pixel & 0b11100000) >> 5
                left_a = (raw_pixel & 0b00010000) >> 4
                right_i = (raw_pixel & 0b00001110) >> 1
                right_a = (raw_pixel & 0b00000001)

                left_color = left_i << 5
                right_color = right_i << 5

                pixels[c, r] = (left_color, left_color, left_color, 255 if left_a == 1 else 0)
                pixels[c + 1, r] = (right_color, right_color, right_color, 255 if right_a == 1 else 0)
    return img


def decode_image_ia8(source_path: pathlib.Path, width: int, height: int) -> Image:
    img = Image.new('RGBA', (width, height), "black")
    pixels = img.load()

    with source_path.open('rb') as raw:
        rdata = raw.read()
        swapped = swap(rdata, width, height, 8)
        data = io.BytesIO(swapped)
        data.seek(0)

        for r in range(0, height):
            for c in range(0, width):
                raw_pixel = int.from_bytes(data.read(1), 'big')
                intensity = raw_pixel & 0b11110000
                alpha = (raw_pixel & 0b00001111) << 4
                pixels[c, r] = (intensity, intensity, intensity, alpha)
    return img


def decode_image_ia16(source_path: pathlib.Path, width: int, height: int) -> Image:
    img = Image.new('RGBA', (width, height), "black")
    pixels = img.load()

    with source_path.open('rb') as raw:
        rdata = raw.read()
        swapped = swap(rdata, width, height, 16)
        data = io.BytesIO(swapped)
        data.seek(0)

        for r in range(0, height):
            for c in range(0, width):
                intensity = int.from_bytes(data.read(1), 'big')
                alpha = int.from_bytes(data.read(1), 'big')
                pixels[c, r] = (intensity, intensity, intensity, alpha)
    return img


def decode_image_ci4(source_path: pathlib.Path, width: int, height: int, tlut_start: bool) -> Image:
    img = Image.new('RGBA', (width, height), "black")
    pixels = img.load()
    tlut = []
    with source_path.open('rb') as raw:
        raw.seek(0 if tlut_start else (int(width / 2) * height))
        while color := raw.read(2):
            tlut.append(rgba5551_decode(color))

        if not tlut_start:
            raw.seek(0)

        swapped = swap(raw.read(), int(width / 2), height, 8)
        data = io.BytesIO(swapped)

        for r in range(0, height):
            for c in range(0, width, 2):
                idx = int.from_bytes(data.read(1), 'big')
                left = (idx & 0b11110000) >> 4
                right = idx & 0b00001111
                pixels[c, r] = tlut[left]
                pixels[c + 1, r] = tlut[right]
    return img


def decode_image_ci8(source_path: pathlib.Path, width: int, height: int, tlut_start: bool) -> Image:
    img = Image.new('RGBA', (width, height), "black")
    pixels = img.load()
    tlut = []
    with source_path.open('rb') as raw:
        raw.seek(0 if tlut_start else width * height)
        while color := raw.read(2):
            tlut.append(rgba5551_decode(color))

        if not tlut_start:
            raw.seek(0)
        swapped = swap(raw.read(), width, height, 8)
        data = io.BytesIO(swapped)

        for r in range(0, height):
            for c in range(0, width):
                idx = int.from_bytes(data.read(1), 'big')
                pixels[c, r] = tlut[idx]
    return img


def encode_image_rgba32(img: Image, width: int, height: int, destination: pathlib.Path):
    buffer = b''
    for r in range(0, height):
        for c in range(0, width):
            buffer += b''.join([x.to_bytes(1, 'little') for x in img.getpixel((c, r))])

    buffer = swap(buffer, width, height, 32)
    with destination.open('wb') as out:
        out.write(buffer)


def encode_image_ia4(img: Image, width: int, height: int, destination: pathlib.Path):
    buffer = b''
    for r in range(0, height):
        for c in range(0, width, 2):
            red, green, blue, alpha = img.getpixel((c, r))
            left_i = red & 0b11100000
            left_a = 0b00010000 if alpha >= 128 else 0

            red, green, blue, alpha = img.getpixel((c + 1, r))
            right_i = (red >> 4) & 0b00001110
            right_a = 0b00000001 if alpha >= 128 else 0

            buffer += (left_i | left_a | right_i | right_a).to_bytes(1, 'big')

    buffer = swap(buffer, int(width / 2), height, 8)
    with destination.open('wb') as out:
        out.write(buffer)


def encode_image_i4(img: Image, width: int, height: int, destination: pathlib.Path):
    buffer = b''
    for r in range(0, height):
        for c in range(0, width, 2):
            red, green, blue, alpha = img.getpixel((c, r))
            left = red & 0b11110000

            red, green, blue, alpha = img.getpixel((c + 1, r))
            right = (red >> 4) & 0b00001111

            buffer += (left | right).to_bytes(1, 'big')

    buffer = swap(buffer, int(width / 2), height, 8)
    with destination.open('wb') as out:
        out.write(buffer)


def encode_image_i8(img: Image, width: int, height: int, destination: pathlib.Path):
    buffer = b''
    for r in range(0, height):
        for c in range(0, width):
            red, green, blue, alpha = img.getpixel((c, r))
            buffer += (red & 0b11111111).to_bytes(1, 'big')

    buffer = swap(buffer, width, height, 8)
    with destination.open('wb') as out:
        out.write(buffer)


def encode_image_ia8(img: Image, width: int, height: int, destination: pathlib.Path):
    buffer = b''

    for r in range(0, height):
        for c in range(0, width):
            red, green, blue, alpha = img.getpixel((c, r))
            intensity = red & 0b11110000
            alpha = (alpha >> 4) & 0b00001111
            buffer += (intensity | alpha).to_bytes(1, 'big')

    buffer = swap(buffer, width, height, 8)
    with destination.open('wb') as out:
        out.write(buffer)


def encode_image_ia16(img: Image, width: int, height: int, destination: pathlib.Path):
    buffer = b''

    for r in range(0, height):
        for c in range(0, width):
            red, green, blue, alpha = img.getpixel((c, r))
            buffer += (red & 0xff).to_bytes(1, 'big')
            buffer += (alpha & 0xff).to_bytes(1, 'big')

    buffer = swap(buffer, width, height, 16)
    with destination.open('wb') as out:
        out.write(buffer)


def encode_image_rgba16(img: Image, width: int, height: int, destination: pathlib.Path):
    buffer = b''

    for r in range(0, height):
        for c in range(0, width):
            red, green, blue, alpha = img.getpixel((c, r))
            buffer += rgba5551_encode(red, green, blue, alpha)

    buffer = swap(buffer, width, height, 16)
    with destination.open('wb') as out:
        out.write(buffer)


def encode_image_ci4(img: Image, width: int, height: int, destination: pathlib.Path, tlut_start: bool):
    tlut = set()

    # building palette...
    for r in range(0, height):
        for c in range(0, width):
            red, green, blue, alpha = img.getpixel((c, r))
            tlut.add(rgba5551_encode(red, green, blue, alpha))

    tlut_index = {v: k for k, v in enumerate(tlut)}
    out_buff = io.BytesIO()
    with out_buff as out_image, destination.open('wb') as out_file:
        for r in range(0, height):
            for c in range(0, width, 2):
                red, green, blue, alpha = img.getpixel((c, r))
                left = tlut_index.get(rgba5551_encode(red, green, blue, alpha))

                red, green, blue, alpha = img.getpixel((c + 1, r))
                right = tlut_index.get(rgba5551_encode(red, green, blue, alpha))

                left = (left << 4) & 0b11110000
                right = right & 0b00001111

                out_image.write((left | right).to_bytes(1, 'big'))
        out_image.seek(0)
        if tlut_start:
            out_file.write(b''.join(tlut_index.keys()))
            out_file.write(b'\x00\x00' * (16 - len(tlut_index)))
            out_file.write(swap(out_image.read(), int(width / 2), height, 8))
        else:
            out_file.write(swap(out_image.read(), int(width / 2), height, 8))
            out_file.write(b''.join(tlut_index.keys()))
            out_file.write(b'\x00\x00' * (16 - len(tlut_index)))


def encode_image_ci8(img: Image, width: int, height: int, destination: pathlib.Path, tlut_start: bool):
    tlut = set()

    # building palette...
    for r in range(0, height):
        for c in range(0, width):
            red, green, blue, alpha = img.getpixel((c, r))
            tlut.add(rgba5551_encode(red, green, blue, alpha))

    tlut_index = {v: k for k, v in enumerate(tlut)}
    out_buff = io.BytesIO()
    with out_buff as out_image, destination.open('wb') as out_file:
        for r in range(0, height):
            for c in range(0, width):
                red, green, blue, alpha = img.getpixel((c, r))
                color = rgba5551_encode(red, green, blue, alpha)
                out_image.write(tlut_index.get(color).to_bytes(1, 'big'))
        out_image.seek(0)
        if tlut_start:
            out_file.write(b''.join(tlut_index.keys()))
            out_file.write(b'\x00\x00' * (256 - len(tlut_index)))
            out_file.write(swap(out_image.read(), width, height, 8))
        else:
            out_file.write(swap(out_image.read(), width, height, 8))
            out_file.write(b''.join(tlut_index.keys()))
            # padding clut
            out_file.write(b'\x00\x00' * (256 - len(tlut_index)))


def save_image_bitmap(texture_path: pathlib.Path, width: int, height: int, dest_path: pathlib.Path, format: str,
                      tlut_start: bool):
    img = None

    if format == "rgba32":
        img = decode_image_rgba32(texture_path, width, height)
    elif format == "rgba16":
        img = decode_image_rgba16(texture_path, width, height)
    elif format == "i4":
        img = decode_image_i4(texture_path, width, height)
    elif format == "i8":
        img = decode_image_i8(texture_path, width, height)
    elif format == "ia4":
        img = decode_image_ia4(texture_path, width, height)
    elif format == "ia8":
        img = decode_image_ia8(texture_path, width, height)
    elif format == "ia16":
        img = decode_image_ia16(texture_path, width, height)
    elif format == "ci4":
        img = decode_image_ci4(texture_path, width, height, tlut_start)
    elif format == "ci8":
        img = decode_image_ci8(texture_path, width, height, tlut_start)

    img.save(dest_path)


def encode_image_texture(bitmap_path: pathlib.Path, width: int, height: int, dest_path: pathlib.Path, format: str,
                         tlut_start: bool):
    image = Image.open(bitmap_path.resolve())
    image = image.convert('RGBA')

    if format == "rgba32":
        encode_image_rgba32(image, width, height, dest_path)
    elif format == "rgba16":
        encode_image_rgba16(image, width, height, dest_path)
    elif format == "i4":
        encode_image_i4(image, width, height, dest_path)
    elif format == "i8":
        encode_image_i8(image, width, height, dest_path)
    elif format == "ia4":
        encode_image_ia4(image, width, height, dest_path)
    elif format == "ia8":
        encode_image_ia8(image, width, height, dest_path)
    elif format == "ia16":
        encode_image_ia16(image, width, height, dest_path)
    elif format == "ci4":
        encode_image_ci4(image, width, height, dest_path, tlut_start)
    elif format == "ci8":
        encode_image_ci8(image, width, height, dest_path, tlut_start)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "format", help="Expected image format.",
        choices=['rgba32', 'rgba16', 'i4', 'i8', 'ia4', 'ia8', 'ia16', 'ci4', 'ci8'])
    parser.add_argument(
        "width", help="Expected image width.", type=int)
    parser.add_argument(
        "height", help="Expected height.", type=int)
    parser.add_argument("filename", help="Path to the source image")

    parser.add_argument('-o', '--output', help="Save the output on a different path")
    parser.add_argument('--swap', action=argparse.BooleanOptionalAction,
                        help="Work on texture with interleaved data, default True")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--tlut-begin', action='store_true',
                       help="Read or place TLUT/palette data at the beginning of the file, valid only for ci4 and ci8")
    # this switch is not actually used since it's the default behaviour, but is importat
    # to keep the user interface consistent
    group.add_argument('--tlut-end', action='store_true',
                       help="Read or place TLUT/palette data at the end of the file, valid only for ci4 and ci8. Default behaviour!")

    args = parser.parse_args()
    if args.swap == False:
        swap.enable = False
    else:
        swap.enable = True

    filename = pathlib.Path(args.filename)
    destination_path = pathlib.Path(args.output) if args.output else None

    if (args.tlut_begin or args.tlut_end) and (args.format not in ('ci4', 'ci8')):
        print('Options like --tlut-begin and --tlut-end are necessary only for ci4/ci8 formats with TLUT data.')
        print()
        parser.print_help()
        sys.exit(-1)

    if not filename.exists():
        print('File does not exists or unreadable: ' + args.filename)
        print()
        parser.print_help()
        sys.exit(-1)

    if filename.suffix.lower() == '.raw' or filename.suffix.lower() == '.bin':
        if destination_path is None:
            destination_path = filename.with_suffix('.png')
        save_image_bitmap(filename, args.width, args.height, destination_path, args.format, args.tlut_begin)

    elif filename.suffix.lower() == '.png':
        if destination_path is None:
            destination_path = filename.with_suffix('.bin')
        encode_image_texture(filename, args.width, args.height, destination_path, args.format, args.tlut_begin)
    else:
        print("Only bitmap RAW/BIN for texture and PNG for images are supported.")
        sys.exit(-1)
