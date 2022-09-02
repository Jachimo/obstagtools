# obstagtools

Some tools for working with Obsidian-flavor (YAML frontmatter + Markdown content) notes files.

## add_tag.py

Simple, quick-and-dirty tool for batch-adding tags to a Markdown document,
meant for scripting.

Minimal dependencies: only `sys`, `argparse`, and `logging`.

### Usage  

- In-place modification: `./add_tag.py targetfile.md -t tag1 tag2`  
- Copy-on-write (safer!): `./add_tag.py targetfile.md copyfile.md -t tag1 tag2`

Tags can be either single-level (e.g. `cats`) or nested (`predators/cats`).
If a desired tag contains spaces, enclose it in double-quotes;
otherwise, tags are assumed to be space-delimited.

**Effect**:  
- _Prepends_ one or more specified tag values (`tag1`, `tag2`) to the list of tags in the YAML frontmatter.

### Help Text

```Text
usage: add_tag.py [-h] [--tag TAG [TAG ...]] [--debug] inpath [outpath]

Add YAML frontmatter tags to Obsidian-style Markdown files

positional arguments:
  inpath                Input file to add tags to
  outpath               Output file to write to (in-place modification if not given)

optional arguments:
  -h, --help            show this help message and exit
  --tag TAG [TAG ...], -t TAG [TAG ...]
                        Tag values to add to the document
  --debug               Enable debug mode (verbose output)
```

Although specifying one or more tags with `--tag` or `-t` is _technically_ optional,
(and the tool will exit with status 0 if none are given), it's not especially useful.
In practical terms, it's a required argument.

### Scripted Use Example

Example goal: add some tags to all Obsidian Markdown (`*.md`) files, 
starting in a specified directory, recursively,
that are 'newer' (have a more recent `mtime`) than a specified file:

```shell
find ~/MyVault.obs/ \
-type f \
-name "*.md" \
-newer ~/MyVault.obs/Travel/san-diego-departure.md \
-exec /path/to/obstagtools/add_tag.py {} -t vacation places/sandiego \;
```

## add_taxonomy.py

This tool updates the metadata fields in an Obsidian document's frontmatter
to match the fields provided in a 'taxonomy' file (by default named `metadata.yaml`
and located in the working directory).

Requires `oyaml` (try `pip install oyaml`).
Future versions will probably switch to `ruamel.yaml` instead.

### Operation

The following rules are used when combining metadata from the document and the
taxonomy file:

- If a field is in the taxonomy _and_ the document frontmatter, include it in the output and and use the document value
- If a field is in taxonomy _but not_ in the document frontmatter, include it and use the taxonomy value
- If a field is in the document frontmatter _but not_ in the taxonomy, then the behavior depends on whether the `--clean` flag is set:
  - IF NOT `--clean`: Include the field and use the document value in the output, effectively passing it through (this is normal operation!)
  - IF `--clean`: Remove the field from the output (destructive operation!)

In short, selecting `--clean` will remove any extraneous metadata from the output, and ensure that the only fields contained in the output's frontmatter are those fields in the taxonomy.

### Usage

Similar to `add_tag.py` (see above), `add_taxonomy.py` can either write to a specified output file, or if one is not provided, it will do an in-place modification of the input file.
This is provided for ease of updating large Obsidian vaults via scripts, but use carefully, and make a backup of the entire vault (if you are not using version control) before starting!

The `--taxonomy` or `-T` argument is optional, and if used should be a path to a taxonomy file, which is basically just a freestanding Obsidian frontmatter section.
If this argument is not supplied, the tool defaults to looking for `metadata.yaml` in the working directory.
An example `metadata.yaml` is provided, and can be used as a starting point for modification.

The `--clean` option is discussed in detail above; if used, it will strip any additional fields that may exist in the input document from the output, if they are not included in the taxonomy.
This might be useful when preparing documents for publication online, but it is off by default.
The default behavior passes through _all_ metadata on the input document, adding fields in order to ensure it conforms to the taxonomy (i.e. all documents' fields will be a superset of the taxonomy).

The `--noindent` option stops the tool from adding two spaces to the beginning of every nested YAML sequence (in Python terms, a list) that is inside a top-level mapping (Python dict).
For Obsidian documents, this mostly affects the `tags` field, which I use with a two-space indent for readability.
Selecing this option results in the output from `yaml.dump()` being written to the output unmolested.

```Text
usage: add_taxonomy.py [-h] [--taxonomy TAXONOMY] [--clean] [--noindent] [--debug] inpath [outpath]

Reformat Obsidian frontmatter to conform to a specified taxonomy

positional arguments:
  inpath                Input file to read from
  outpath               Output file to write to (if not provided, modify input file in-place)

optional arguments:
  -h, --help            show this help message and exit
  --taxonomy TAXONOMY, -T TAXONOMY
                        YAML taxonomy file (default: metadata.yaml)
  --clean               Remove all input document fields not present in taxonomy (DESTRUCTIVE!)
  --noindent            Do not indent YAML sequences (may break other tools)
  --debug               Enable debug mode (verbose output)
```
## Additional Notes

### Required Structure

The specified input file must be a "well formed" YAML+Markdown document, consisting of: 

- The string `---\n` (that's three hyphens, followed by a line ending character such as LF), **and nothing else**, on the first line of the file; followed by 
- YAML data, specifically containing a sequence named 'tags' with one or more values, represented using block-style YAMP (_not_ flow!) syntax_; then
- Another `---` on a line by itself (note this is _not_ valid YAML, and marks the end of the YAML frontmatter)
- The content, formatted with Markdown
- EOF

## YAML Block vs. Flow Style

**YAML Block Style**  
This is the style I use for all Obsidian tags.

```yaml
---
tags:
  - toys
  - gifts
---
# Heading
Content begins here...
```

**YAML Flow Style**  
Alternative, compact style that is still valid YAML, but handling
it is not a very high priority for these tools. 
This is particularly the case for the tools
designed to have minimal dependencies, which don't have an actual
YAML parser.

```yaml
---
tags: [toys, gifts]
---
# Heading
Content begins here...
```
