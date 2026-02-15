# wp-block-markup — Claude Skill

A [Claude skill](https://support.anthropic.com/en/articles/11147075-what-are-skills) that converts Markdown files to WordPress block markup (Gutenberg serialized HTML) — and serves as a block grammar reference for Claude to consult when working with WordPress content.

## What it does

- Converts `.md` files to block-delimited HTML that can be pasted directly into the WordPress **Code Editor** (Ctrl+Shift+Alt+M) or used in block theme template files.
- Gives Claude a quick-reference for the block comment syntax so it produces correct markup without searching the web each time.
- Handles: headings, paragraphs, fenced code blocks (with language attributes), ordered/unordered lists, blockquotes, tables, horizontal rules, and inline formatting (bold, italic, code, links).

## Install as a Claude skill

1. In [claude.ai](https://claude.ai), open **Settings → Profile → Custom Skills** (or drop files into a Project's knowledge).
2. Upload both:
   - `SKILL.md`
   - `scripts/md_to_blocks.py`
3. That's it — Claude will use the skill whenever you ask it to convert Markdown to WordPress block markup.

The directory layout Claude expects:

```
/mnt/skills/user/wp-block-markup/
├── SKILL.md
└── scripts/
    └── md_to_blocks.py
```

## Use standalone (no Claude needed)

The converter is a plain Python 3 script with no dependencies:

```bash
python3 scripts/md_to_blocks.py input.md output.html
```

It prints a summary of block counts when finished:

```
Converted to 231 blocks:
  wp:list-item: 83
  wp:paragraph: 71
  wp:list: 27
  wp:heading: 20
  wp:separator: 17
  wp:code: 11
  wp:quote: 1
  wp:table: 1
```

## Example

**Input** (`example.md`):

```markdown
# Hello World

A paragraph with **bold** and `inline code`.

## Section One

- First item
- Second item with a [link](https://example.com)
```

**Output** (`example.html`):

```html
<!-- wp:heading {"level":1} -->
<h1 class="wp-block-heading">Hello World</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>A paragraph with <strong>bold</strong> and <code>inline code</code>.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Section One</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul class="wp-block-list">
<!-- wp:list-item -->
<li>First item</li>
<!-- /wp:list-item -->
<!-- wp:list-item -->
<li>Second item with a <a href="https://example.com">link</a></li>
<!-- /wp:list-item -->
</ul>
<!-- /wp:list -->
```

## Block grammar quick reference

See [`SKILL.md`](SKILL.md) for the full reference. The essentials:

| Block | Opening comment | Needs attributes? |
|-------|----------------|-------------------|
| Paragraph | `<!-- wp:paragraph -->` | No |
| Heading (h2) | `<!-- wp:heading -->` | No (h2 is default) |
| Heading (other) | `<!-- wp:heading {"level":3} -->` | Yes |
| Code | `<!-- wp:code -->` | No |
| List (unordered) | `<!-- wp:list -->` | No |
| List (ordered) | `<!-- wp:list {"ordered":true} -->` | Yes |
| List item | `<!-- wp:list-item -->` | No |
| Quote | `<!-- wp:quote -->` | No |
| Table | `<!-- wp:table -->` | No |
| Separator | `<!-- wp:separator -->` | No |
| Image | `<!-- wp:image {"sizeSlug":"large"} -->` | Typically yes |

## Related resources

- [Markup representation of a block](https://developer.wordpress.org/block-editor/getting-started/fundamentals/markup-representation-block/) — official WordPress docs
- [Block grammar basics](https://fullsiteediting.com/lessons/block-grammar-basics/) — Full Site Editing course
- [dmsnell/html-to-md](https://github.com/dmsnell/html-to-md/) — the reverse direction (HTML→Markdown) using WordPress' HTML API
- [wpblockdocs.com](https://wpblockdocs.com) — searchable block HTML reference
- [Block markup cheat sheet](https://github.com/jeffreyducharme/wp-gutenberg-block-markup-cheat-sheet) — regex patterns for batch conversion

## License

MIT
