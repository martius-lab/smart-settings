def removesuffix(self: str, suffix: str) -> str:
    # suffix='' should not call self[:-0].
    if suffix and self.endswith(suffix):
        return self[: -len(suffix)]
    else:
        return self[:]
