import shortuuid


def new_id(prefix: str) -> str:
    return f"{prefix}_{shortuuid.uuid()}"
