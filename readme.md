# NHB Post Generator

Lazy work to generate Instagram post images for Nyon Handball La Côte out of
the [official ics calendar retrieved from the FSH website](https://www.handball.ch/fr/matchcenter/vereine/330442#/schedule).

## Setup

* If you don't have git installed (should be ok on ,acOS), [download it](https://git-scm.com/downloads) and install it.
  Even older version should fit the bill.
* Requires a recent `python` (and `pip`) version. Developed with `3.12`.
* To avoid the pain of installing `cairo` this tool need [Inkscape](https://inkscape.org) to generate the png out of the
  svg. It was developed with `1.3.2`.
* If you did not install Inkscape in the classic place, update its path at the beginning of the script (TODO: config
  file).

Then run:

```
git clone https://github.com/paulbombarde/NHBPostGenerator.git
cd NHBPostGenerator
pip install -r requirements.txt
```

## Usage

Download the relevant calendar from the [FSH website](https://www.handball.ch/fr/matchcenter/vereine/330442#/schedule),
then run

```
python generator.py <path_to_ics>
```

It will generate the posts and stories in the `outputs/png` folder. In the `outputs/svg` folder, you can find the
intermediate files, as well as the results files to be updated and re-exported when the matches are played. The output
files
are organized by dates and should be easy to sort out. To simplify life, only files from the current date are generated.

## Templates

Templates are expected to be svg edited by Inkscape and exported as `Inkscape SVG`. Texts (and logos) to be replaced are
expected to be tagged as `inkscape:label`.

## Logic

1. Parses the ics input file, group matches by dates.
2. Group matches H1 / D3 / Rest
3. Open the corresponding templates, searches for specific `inkscape:label` value.
    1. In each of those, get the underlying `svg:span` and replace the associated text.
    2. Some replacements occur for well known places, clubs...
    3. Clubs logos are retrieved from the repo assets. The logos provided by the FSH are very bad quality.