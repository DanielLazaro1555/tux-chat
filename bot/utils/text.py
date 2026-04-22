"""Text utilities for message handling."""

# Telegram message character limit
MAX_MESSAGE_LEN = 4096


def split_long_message(text: str, limit: int = MAX_MESSAGE_LEN) -> list[str]:
    """
    Split a long message into chunks of at most `limit` characters.

    Preserves words when possible (splits on spaces if within limit).
    If a word itself exceeds the limit, it will be forcibly split.

    Args:
        text: The message to split
        limit: Maximum characters per chunk (default 4096)

    Returns:
        List of message chunks ready to send
    """
    if len(text) <= limit:
        return [text]

    chunks = []
    current_chunk = ""

    # Split by spaces to preserve words
    words = text.split(" ")

    for word in words:
        # If word alone exceeds limit, split it forcefully
        if len(word) > limit:
            # First, finish current chunk if any
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            # Break the long word into fixed-size pieces
            for i in range(0, len(word), limit):
                chunks.append(word[i : i + limit])
            continue

        # Try adding word to current chunk
        test_chunk = f"{current_chunk} {word}" if current_chunk else word
        if len(test_chunk) <= limit:
            current_chunk = test_chunk
        else:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = word

    # Append last chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def truncate_to_limit(
    text: str, limit: int = MAX_MESSAGE_LEN, suffix: str = "..."
) -> str:
    """
    Truncate text to exact limit, optionally adding suffix.
    Useful for previews or when splitting is not desired.
    """
    if len(text) <= limit:
        return text
    return text[: limit - len(suffix)] + suffix
