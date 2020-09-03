def is_available() -> bool:
    try:
        import tornado
        return True
    except ImportError:
        return False
