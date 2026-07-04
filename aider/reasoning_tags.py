#!/usr/bin/env python

import re

from aider.dump import dump  # noqa

# Standard tag identifier
REASONING_TAG = "thinking-content-" + "7bbeb8e1441453ad999a0bbba8a46d4b"
# Output formatting
REASONING_START = "--------------\n► **THINKING**"
REASONING_END = "------------\n► **ANSWER**"


def remove_reasoning_content(res, reasoning_tag):
    """
    Remove reasoning content from text based on tags.

    Args:
        res (str): The text to process
        reasoning_tag (str): The tag name to remove

    Returns:
        str: Text with reasoning content removed
    """
    if not reasoning_tag:
        return res

    open_tag = f"<{reasoning_tag}>"
    closing_tag = f"</{reasoning_tag}>"
    # Whether the response contained an opening tag. Captured before the
    # balanced-block substitution below removes it.
    had_open_tag = open_tag in res

    # Try to match the complete tag pattern first
    pattern = f"<{reasoning_tag}>.*?</{reasoning_tag}>"
    res = re.sub(pattern, "", res, flags=re.DOTALL).strip()

    # Only treat a remaining closing tag as an orphan reasoning close when no
    # opening tag was present at all (e.g. a continuation whose opening tag
    # was emitted in a prior chunk); in that case the text before it is
    # reasoning and is dropped. If there was an opening tag, any closing tag
    # still left after the substitution above is a *literal* occurrence in
    # the model's answer (e.g. inside code or prose) and must be preserved.
    if not had_open_tag and closing_tag in res:
        # Split on the closing tag and keep everything after it
        parts = res.split(closing_tag, 1)
        res = parts[1].strip() if len(parts) > 1 else res

    return res


def replace_reasoning_tags(text, tag_name):
    """
    Replace opening and closing reasoning tags with standard formatting.
    Ensures exactly one blank line before START and END markers.

    Args:
        text (str): The text containing the tags
        tag_name (str): The name of the tag to replace

    Returns:
        str: Text with reasoning tags replaced with standard format
    """
    if not text:
        return text

    # Replace opening tag with proper spacing
    text = re.sub(f"\\s*<{tag_name}>\\s*", f"\n{REASONING_START}\n\n", text)

    # Replace closing tag with proper spacing
    text = re.sub(f"\\s*</{tag_name}>\\s*", f"\n\n{REASONING_END}\n\n", text)

    return text


def format_reasoning_content(reasoning_content, tag_name):
    """
    Format reasoning content with appropriate tags.

    Args:
        reasoning_content (str): The content to format
        tag_name (str): The tag name to use

    Returns:
        str: Formatted reasoning content with tags
    """
    if not reasoning_content:
        return ""

    formatted = f"<{tag_name}>\n\n{reasoning_content}\n\n</{tag_name}>"
    return formatted
