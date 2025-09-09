import dendrite.utils.constants as constants

def clean_path(path: str) -> str:
    return path.replace(constants.DIARRHEA_ROOT, "")
