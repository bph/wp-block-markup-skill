---
name: wp-block-markup
description: Convert Markdown files to WordPress block markup (Gutenberg serialized HTML). Use whenever the user wants to produce content that can be pasted into the WordPress Code Editor or used in block theme HTML templates. Also use for the reverse direction (block markup to markdown).
---

# WordPress Block Markup Converter

Convert between Markdown and WordPress block markup (the serialized HTML comment format used by Gutenberg).

## When to use

- User asks to convert a `.md` file to WordPress block notation / Gutenberg markup
- User wants content they can paste into the WordPress **Code Editor** (Ctrl+Shift+Alt+M)
- User is building HTML templates for a block theme and needs properly delimited blocks
- User wants to convert block markup back to readable Markdown

## How to use

Run the Python converter script bundled with this skill:

```bash
python3 /mnt/skills/user/wp-block-markup/scripts/md_to_blocks.py <input.md> <output.html>
```

The script handles: headings, paragraphs, fenced code blocks, ordered/unordered lists, blockquotes, tables, horizontal rules, and all inline formatting (bold, italic, code, links).

### Quick integration pattern

```python
import subprocess
result = subprocess.run(
    ["python3", "/mnt/skills/user/wp-block-markup/scripts/md_to_blocks.py", input_path, output_path],
    capture_output=True, text=True
)
print(result.stdout)  # Block count stats
```

## Block grammar reference

WordPress block markup wraps HTML in comment delimiters. Every block has an opening comment and either a closing comment or is self-closing.

### Core block patterns

**Paragraph**
```html
<!-- wp:paragraph -->
<p>Text with <strong>bold</strong> and <a href="url">links</a>.</p>
<!-- /wp:paragraph -->
```

**Heading** (h2 is default, others need `level` attribute)
```html
<!-- wp:heading -->
<h2 class="wp-block-heading">Section title</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Sub-section</h3>
<!-- /wp:heading -->
```

**Code block**
```html
<!-- wp:code -->
<pre class="wp-block-code"><code lang="php" class="language-php">echo 'hello';</code></pre>
<!-- /wp:code -->
```

**Unordered list** (each item gets its own block comment)
```html
<!-- wp:list -->
<ul class="wp-block-list">
<!-- wp:list-item -->
<li>First item</li>
<!-- /wp:list-item -->
<!-- wp:list-item -->
<li>Second item</li>
<!-- /wp:list-item -->
</ul>
<!-- /wp:list -->
```

**Ordered list**
```html
<!-- wp:list {"ordered":true} -->
<ol class="wp-block-list">
<!-- wp:list-item -->
<li>Step one</li>
<!-- /wp:list-item -->
</ol>
<!-- /wp:list -->
```

**Blockquote** (inner content uses nested paragraph blocks)
```html
<!-- wp:quote -->
<blockquote class="wp-block-quote">
<!-- wp:paragraph -->
<p>Quoted text here.</p>
<!-- /wp:paragraph -->
</blockquote>
<!-- /wp:quote -->
```

**Table**
```html
<!-- wp:table -->
<figure class="wp-block-table"><table><thead><tr>
<th>Header 1</th>
<th>Header 2</th>
</tr></thead><tbody>
<tr>
<td>Cell 1</td>
<td>Cell 2</td>
</tr>
</tbody></table></figure>
<!-- /wp:table -->
```

**Separator / horizontal rule**
```html
<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->
```

**Image**
```html
<!-- wp:image {"sizeSlug":"large"} -->
<figure class="wp-block-image size-large">
    <img src="source.jpg" alt="" />
</figure>
<!-- /wp:image -->
```

**Self-closing / dynamic blocks** (no inner HTML)
```html
<!-- wp:search /-->
<!-- wp:latest-posts {"postsToShow":4,"displayPostDate":true} /-->
```

### Key rules

1. Core blocks use `wp:blockname` (no `core/` prefix). Custom blocks use `wp:namespace/blockname`.
2. Block attributes are a JSON object inside the opening comment: `<!-- wp:heading {"level":3} -->`.
3. The opening and closing comments wrap the HTML output of the block.
4. Content inside code blocks must be HTML-escaped (`&lt;`, `&gt;`, `&amp;`, `&quot;`).
5. Lists require `<!-- wp:list-item -->` wrappers around each `<li>`.
6. Blockquotes contain nested `<!-- wp:paragraph -->` blocks for their inner content.
7. Tables live inside a `<figure class="wp-block-table">` wrapper.

### Helpful references

- [Markup representation of a block](https://developer.wordpress.org/block-editor/getting-started/fundamentals/markup-representation-block/) — official docs
- [Block grammar basics](https://fullsiteediting.com/lessons/block-grammar-basics/) — Full Site Editing course
- [dmsnell/html-to-md](https://github.com/dmsnell/html-to-md/) — HTML→Markdown using the WordPress HTML API (reverse direction reference)
- [wp-block-docs](https://wpblockdocs.com) — searchable block HTML reference
- [jeffreyducharme/wp-gutenberg-block-markup-cheat-sheet](https://github.com/jeffreyducharme/wp-gutenberg-block-markup-cheat-sheet) — cheat sheet with regex patterns

## Output

The converter produces an `.html` file containing serialized block markup ready for:
- Pasting into the WordPress Code Editor
- Use in block theme HTML template files (`templates/`, `parts/`)
- Import via WP-CLI or the REST API
