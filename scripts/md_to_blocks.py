#!/usr/bin/env python3
"""Convert Markdown to WordPress block markup (Gutenberg serialized HTML).

Usage:
    python3 md_to_blocks.py <input.md> <output.html>

Produces an HTML file containing WordPress block comment delimiters
that can be pasted into the Code Editor or used in block theme templates.
"""

import re
import sys
import html as html_module
import collections


def convert_inline(text):
    """Convert inline Markdown formatting to HTML."""
    # Links: [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Bold+italic: ***text***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic: *text* (avoid matching inside HTML tags)
    text = re.sub(r'(?<![<\w/])(\*)([^*\n]+?)\1', r'<em>\2</em>', text)
    # Inline code: `text`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def md_to_blocks(md_text):
    """Parse Markdown and return WordPress block markup as a string."""
    lines = md_text.split('\n')
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # --- Blank line ---
        if line.strip() == '':
            i += 1
            continue

        # --- Horizontal rule / separator ---
        if line.strip() == '---':
            out.append('<!-- wp:separator -->')
            out.append('<hr class="wp-block-separator has-alpha-channel-opacity"/>')
            out.append('<!-- /wp:separator -->')
            out.append('')
            i += 1
            continue

        # --- Headings ---
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            text = convert_inline(m.group(2))
            if level == 2:
                out.append('<!-- wp:heading -->')
            else:
                out.append(f'<!-- wp:heading {{"level":{level}}} -->')
            out.append(f'<h{level} class="wp-block-heading">{text}</h{level}>')
            out.append('<!-- /wp:heading -->')
            out.append('')
            i += 1
            continue

        # --- Fenced code block ---
        if line.strip().startswith('```'):
            lang = line.strip()[3:].strip()
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1  # skip closing ```
            code_content = '\n'.join(code_lines)
            escaped = html_module.escape(code_content)
            out.append('<!-- wp:code -->')
            if lang:
                out.append(f'<pre class="wp-block-code"><code lang="{lang}" class="language-{lang}">{escaped}</code></pre>')
            else:
                out.append(f'<pre class="wp-block-code"><code>{escaped}</code></pre>')
            out.append('<!-- /wp:code -->')
            out.append('')
            continue

        # --- Blockquote ---
        if line.startswith('> '):
            quote_lines = []
            while i < n and lines[i].startswith('> '):
                quote_lines.append(lines[i][2:])
                i += 1
            quote_text = convert_inline(' '.join(quote_lines))
            out.append('<!-- wp:quote -->')
            out.append('<blockquote class="wp-block-quote">')
            out.append('<!-- wp:paragraph -->')
            out.append(f'<p>{quote_text}</p>')
            out.append('<!-- /wp:paragraph -->')
            out.append('</blockquote>')
            out.append('<!-- /wp:quote -->')
            out.append('')
            continue

        # --- Table ---
        if '|' in line and i + 1 < n and re.match(r'^\|[\s\-:|]+\|$', lines[i + 1].strip()):
            header_line = line
            i += 2  # skip header + separator
            rows = []
            while i < n and '|' in lines[i] and lines[i].strip().startswith('|'):
                rows.append(lines[i])
                i += 1
            header_cells = [c.strip() for c in header_line.strip().strip('|').split('|')]
            out.append('<!-- wp:table -->')
            out.append('<figure class="wp-block-table"><table><thead><tr>')
            for cell in header_cells:
                out.append(f'<th>{convert_inline(cell)}</th>')
            out.append('</tr></thead><tbody>')
            for row in rows:
                cells = [c.strip() for c in row.strip().strip('|').split('|')]
                out.append('<tr>')
                for cell in cells:
                    out.append(f'<td>{convert_inline(cell)}</td>')
                out.append('</tr>')
            out.append('</tbody></table></figure>')
            out.append('<!-- /wp:table -->')
            out.append('')
            continue

        # --- Unordered list ---
        if re.match(r'^- ', line):
            items = []
            while i < n and (re.match(r'^- ', lines[i]) or
                             (lines[i].startswith('  ') and not re.match(r'^- ', lines[i]))):
                if re.match(r'^- ', lines[i]):
                    items.append(lines[i][2:])
                else:
                    items[-1] += ' ' + lines[i].strip()
                i += 1
            out.append('<!-- wp:list -->')
            out.append('<ul class="wp-block-list">')
            for item in items:
                out.append('<!-- wp:list-item -->')
                out.append(f'<li>{convert_inline(item)}</li>')
                out.append('<!-- /wp:list-item -->')
            out.append('</ul>')
            out.append('<!-- /wp:list -->')
            out.append('')
            continue

        # --- Ordered list ---
        if re.match(r'^\d+\.\s', line):
            items = []
            while i < n and (re.match(r'^\d+\.\s', lines[i]) or
                             (lines[i].startswith('  ') and not re.match(r'^\d+\.\s', lines[i]))):
                if re.match(r'^\d+\.\s', lines[i]):
                    items.append(re.sub(r'^\d+\.\s', '', lines[i]))
                else:
                    items[-1] += ' ' + lines[i].strip()
                i += 1
            out.append('<!-- wp:list {"ordered":true} -->')
            out.append('<ol class="wp-block-list">')
            for item in items:
                out.append('<!-- wp:list-item -->')
                out.append(f'<li>{convert_inline(item)}</li>')
                out.append('<!-- /wp:list-item -->')
            out.append('</ol>')
            out.append('<!-- /wp:list -->')
            out.append('')
            continue

        # --- Paragraph (default) ---
        para_lines = []
        while i < n and lines[i].strip() != '':
            if (lines[i].startswith('#') or
                lines[i].strip().startswith('```') or
                lines[i].strip() == '---' or
                lines[i].startswith('> ') or
                re.match(r'^- ', lines[i]) or
                re.match(r'^\d+\.\s', lines[i])):
                break
            if ('|' in lines[i] and i + 1 < n and
                    re.match(r'^\|[\s\-:|]+\|$', lines[i + 1].strip())):
                break
            para_lines.append(lines[i])
            i += 1

        if para_lines:
            # Detect metadata-style fields (**Who:** / **Where:**) — join with <br>
            all_fields = all(
                re.match(r'^\*\*\w', pl.strip())
                for pl in para_lines if pl.strip()
            )
            if all_fields and len(para_lines) > 1:
                text = '<br>'.join(convert_inline(pl) for pl in para_lines)
            else:
                text = ' '.join(convert_inline(pl) for pl in para_lines)

            out.append('<!-- wp:paragraph -->')
            out.append(f'<p>{text}</p>')
            out.append('<!-- /wp:paragraph -->')
            out.append('')

    return '\n'.join(out)


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.md> <output.html>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, 'r', encoding='utf-8') as f:
        md = f.read()

    blocks = md_to_blocks(md)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(blocks)

    # Print stats
    types = re.findall(r'<!-- wp:(\w[\w-]*)', blocks)
    counts = collections.Counter(types)
    total_blocks = sum(1 for t in types if not t.startswith('/'))
    print(f"Converted to {total_blocks} blocks:")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  wp:{k}: {v}")


if __name__ == '__main__':
    main()
