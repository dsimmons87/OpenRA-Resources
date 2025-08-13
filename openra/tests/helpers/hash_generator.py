import hashlib


class UniqueHashGenerator:
    """
    Unique hash generator for testing.
    
    This prevents hash collisions between different test files
    by using a global counter that is incremented across all tests.
    """
    _counter = 0
    
    @classmethod
    def get_unique_hash(cls):
        """Generate a unique 40-character SHA-1 hash for testing"""
        cls._counter += 1
        return hashlib.sha1(str(cls._counter).encode()).hexdigest()
