import hashlib

def get_sha1_hash(file_path):
    """
    Calculates and returns the SHA1 hash of a local file.

    Args:
        file_path (str): The path to the file to calculate the hash for.

    Returns:
        str: The SHA1 hash of the file, or an error message if the file could not be read.
    """
    sha1_hash = hashlib.sha1()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha1_hash.update(chunk)
        return sha1_hash.hexdigest()
    except Exception as e:
        error = (f'Error calculating SHA1 for {file_path}: {e}')
        return error

def get_sha256_hash(file_path):
    """
    Calculates and returns the SHA256 hash of a local file.

    Args:
        file_path (str): The path to the file to calculate the hash for.

    Returns:
        str: The SHA256 hash of the file, or an error message if the file could not be read.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        error = (f'Error calculating SHA256 for {file_path}: {e}')
        return error
