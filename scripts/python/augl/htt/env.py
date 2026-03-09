"""
Augl environment variables.
"""

import os


class Environent:
    """
    Augl environment variables.
    """

    BASE_DIR: str = os.environ.get("AUGL_HTT_BASEDIR", "")
    REPO_NAME: str = os.environ.get("AUGL_HTT_REPO_NAME", "")
    USER_PREF_DIR: str = os.environ.get("HOUDINI_USER_PREF_DIR", "")
