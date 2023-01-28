[![Docker Repository on Quay](https://quay.io/repository/loadwordteam/picflip64/status "Docker Repository on Quay")](https://quay.io/repository/loadwordteam/picflip64)
# Picflip64

PicFlip64 is a tool for converting texture files for Nintendo
64 into PNG files. You might find this tool useful if you're working
on a fan translation or a mod for a game.

This tool makes it possibile to convert the following texture formats
to PNG, or vice versa:

- rgba32
- rgba16
- i4
- i8
- ia4
- ia8
- ia16
- ci4
- ci8

For texture formats like ci4 and ci8, you need to specify where to
read the TLUT data. This palette information is usually at the
beginning or the end of the file. Picflip64 by default assumes such
data is at the end, but you can control this aspect!

This tool supports texture with interleaved data, some games like
Conker's Bad Fur Day and Diddy Kong Racing use this trick.

## Requirements and installation

You need Python >= 3.9 installed and Pillow, you can install the
library with the following commands

```
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

You can also install Pillow using the package manager of your
distribution, this tool is not very picky about the version!

## Usage

Picflip64 doesn't automatically recognise the format of the texture,
so it's necessay to specify it manually like the following example:

```
python picflip64 ci8 64 64 some-texture.raw
```

If everything goes well, you will find a file named `some-texture.png`
in the same directory of the texture. You can go back to convert the
image to the texture in the same way.

```
python picflip64 ci8 64 64 some-texture.png
```

Since the example is dealing with ci8 format, picflip64 assumes the
TLUT data is at the end of the file, if it's not the case, you can
read the palette at the beginning in this way

```
python picflip64 ci8 64 64 some-texture.raw --tlut-begin
```

you will also need to define the flag when you convert back the image

```
python picflip64 ci8 64 64 some-texture-done.png --tlut-begin
```

If you want, there is also `--tlut-end`, usually there is no need to
specify it but you might want to use it anyway.

You don't need to define any TLUT data for other formats, just `ci4`
and `ci8` are a special case.

### I suggest to always use the `--output` switch!

**Be careful**, the tool used like that will overwrite the original
texture, it's better to specify where the tool should write the file
with the `--output` parameter, like this:

```
python picflip64 rgba16 64 64 some-texture.raw --output converted/some-path.png
python picflip64 rgba16 64 64 translated/some-texture.png --output build/texture.bin
```

### Interleaved (or swapped) data

As mentioned before, this tool supports textures with interleaved
data, by default it assumes the texture has the data arranged in this
way. You can inspect the texture and check if it's interleaved with
tools like [Texture64](https://github.com/queueRAM/Texture64).

You can control this aspect during the conversion with the options
`--no-swap` and `--swap`. Remember, by default the tool assumes the
data is interleaved!

| Case | Image |
|------|--------|
| Texture not interleaved or the data has been handled during the conversion | ![optimised data](./rulesless.png) |
| Texture interleaved, game data is optimised! | ![not optimised data](./rulesless-swap.png) |


## Changelog

### 1.0

First public release, this tool was specifically made to help the fan
translation of Conker's Bad Fur Day!

## Contributors

- Infrid
- [Rulesless](https://letraduzionidirulesless.wordpress.com/)

### Special thanks to

Rulesless, for requesting the creation of the tool and for giving tips
on how to improve it and for helping out with the testing.

Thanks to the staff of N64Squid and their [exhaustive
information](https://n64squid.com/homebrew/n64-sdk/textures/image-formats/)
about texture formats.

Huge shout out to _mkst_ over the N64 decomp discord for providing a
small snippet on how deal with interleaved data.

Thanks to you for using this tool!

## Contacts

Gianluigi "Infrid" Cusimano <infrid@infrid.com>

https://loadwordteam.com/

[![a project by load word team](https://loadwordteam.com/logo-lwt-small.png "a project by load word team")](https://loadwordteam.com)


