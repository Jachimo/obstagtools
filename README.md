# obstagtools

Some tools for working with Obsidian-flavor (YAML frontmatter + Markdown content) notes files.

## add_tag.py

Quick-and-dirty tool for batch-adding tags to a Markdown document,
meant for scripting.

Very minimal dependencies (only `sys`, `argparse`, and `logging`).

**Usage:**  
- In-place modification: `./add_tag.py targetfile.md -t tag1 tag2`  
- Copy-on-write (safer!): `./add_tag.py targetfile.md copyfile.md -t tag1 tag2`

Tags can be either single-level (e.g. `cats`) or nested (`predators/cats`).
If a desired tag contains spaces, enclose it in double-quotes;
otherwise, tags are assumed to be space-delimited.

**Effect**:  
- _Prepends_ one or more specified tag values (`tag1`, `tag2`) to the list of tags in the YAML frontmatter.

The specified input file must be a "well formed" YAML+Markdown document, consisting of: 

- The string `---` on a line by itself (i.e. three hyphens, followed by a line ending character),
- YAML frontmatter, specifically containing a sequence named 'tags' with one or more values, _using indented (not inline-block) notation_.
- Another `---` on a line by itself
- The content, formatted with Markdown

Note the restriction on indented notation only for "tags". 
This (theoretically) works:

```yaml
---
tags:
  - toys
  - gifts
---
# Heading
Content begins here...
```

But currently this _does not_:
```yaml
---
tags: [toys, gifts]
---
# Heading
Content begins here...
```
### Scripting Examples

Example: add some tags to all Obsidian Markdown (`*.md`) files, 
starting in a specified directory, recursively,
that are newer than a specified file:

```shell
find ~/MyVault.obs/ \
-type f \
-name "*.md" \
-newer ~/MyVault.obs/Travel/san-diego-departure.md \
-exec /path/to/obstagtools/add_tag.py {} -t vacation places/sandiego \;
```
