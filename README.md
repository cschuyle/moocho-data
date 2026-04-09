# Moocho Data

This is where Moocho (Morsor) get their data.

This repo is the source of truth for
- Structure of the data files

This repo contains tools to manage data to be used in Moocho/Morsor.


## Requirements
- Python 3
- `jq`

## In Brief

Moocho consumes **troves**. Troves consist of **items**. Items have at minimum a title. Other fun stuff include:
- Thumbnail
- Large image
- Link to URL
- Accompanying files (images, documents, videos, audio, etc.)

Many troves are populated by importing exports from external sources. That's mainly what this repo is about: Converting from external to internal format, and managing the resulting data for consumption by a Moocho-based app (some of you will want to call the apps "clients").


## Internal formats


### `littlePrinceItem`

> An overlapping set of the information you'd expect a book to have. Specifically, includes data about language, translator, illustrator.

There are other formats but no tools in this repo yet make use of them. Stay tuned!


## Supported external formats

| Format | Tool | Notes |
| --- | --- | --- |
| RIS | `ris2moocho.py` | [Wikipedia: RIS (file format)](https://en.wikipedia.org/wiki/RIS_%28file_format%29). |


## Usage

The root directory contains executables. Each tries to be self-explanatory via `<executable> --help`

## Local development

`make`: Run all tests
