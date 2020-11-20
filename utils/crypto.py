from hashlib import md5

__all__ = ['get_md5_hex_hash']


def get_md5_hex_hash(text: str) -> str:
    """
    >>> get_md5_hex_hash("abc18")
    '...cc38887a5...'
    >>> get_md5_hex_hash("abc39")
    '...eee...'
    >>> get_md5_hex_hash("abc816")
    '...eeeee...'
    """
    return md5(text.encode()).digest().hex()
