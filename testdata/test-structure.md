---
created: "2022-08-30 23:30 EDT"
testvalue: False
tags:
  - testfile
  - example
  - programming/yaml
alias: "Sample Obsidian Document"
name: "Structure Test Document"
---
# Sample Obsidian Structured Text Document
This is a sample of a structured text document using an Obsidian-style
(also Jekyll-style) YAML "frontmatter" section, followed by
Markdown-styled content.

## Some Examples
Here we're just exercising the Markdown functionality...

- Top Level List
  - Second Level List
  - Second Level List (continued)
  - Attachment in a list: [[foo.txt]]
- [[Top Level List Part Deux]]
- Top Level List: [[The Return of the List]] (another internal wiki-link)
- [An external link](https://www.google.com) with inline notation
- [And another external link][re] with footnote-style notation
  - But not an actual footnote[^1]

[re]: https://regex101.com/

Are you sure that `2 + 2 = 4`?

Embedded image (with width set):  
![[bar.png|250]]

**A Wise Quotation:**  

> You may go into the fields or down the lane, but don’t go into
> Mr. McGregor’s garden. Your Father had an accident there; he was put
> in a pie by Mrs. McGregor.

[^1]: They're written like this.
