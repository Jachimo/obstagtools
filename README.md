# obstagtools

Quick tools for working with Obsidian-flavor (YAML frontmatter + Markdown content) notes files.

## add_tag.py

Quick-and-dirty tool for mass-adding tags to a Markdown document,
meant for scripting.

Very minimal dependencies (only `sys`, `argparse`, and `logging`).

**Usage** (in-place modification): `./add_tag.py targetfile.md -t tag1 tag2`  
Or to create a copy on write (safer!): `./add_tag.py targetfile.md copyfile.md -t tag1 tag2`

**Effect**: Prepends one or more specified tag values (`tag1`, `tag2`) to the list of tags in the YAML frontmatter.

The specified input file must be a "well formed" YAML+Markdown document, consisting of: 

- The string `---` on a line by itself (followed by a line ending character),
- YAML frontmatter, specifically containing a sequence named 'tags' with one or more values, _using indented (not inline-block) notation_.
- Another `---` on a line by itself (followed by a line ending char)
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

