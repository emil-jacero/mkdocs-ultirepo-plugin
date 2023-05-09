import logging
import shutil
from pathlib import Path
from tempfile import mkdtemp

from mkdocs.utils import warning_filter

log = logging.getLogger(__name__)
log.addFilter(warning_filter)

class Merger:
    def __init__(self, config, merged_docs_dir=None):
        pass