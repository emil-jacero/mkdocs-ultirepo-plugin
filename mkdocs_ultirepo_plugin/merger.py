import logging
import shutil
from pathlib import Path
from tempfile import mkdtemp

from mkdocs.utils import warning_filter

log = logging.getLogger(__name__)
log.addFilter(warning_filter)

class Merger:
    def __init__(self, config, merged_docs_dir=None):
        self.orig_docs_dir = config['docs_dir']
        self.merged_docs_dir = merged_docs_dir or mkdtemp()
        self.files_source_dir = {}

    def _copy_original(self):
        orig_docs_path = Path(self.orig_docs_dir)
        merged_docs_path = Path(self.merged_docs_dir)

        for item in orig_docs_path.iterdir():
            if item.is_file():
                shutil.copy2(item, merged_docs_path)
            elif item.is_dir():
                shutil.copytree(item, merged_docs_path / item.name)

    def _append(self, orig_docs_dir, orig_docs_sub_dir):
        orig_docs_dir = Path(orig_docs_dir)
        orig_docs_sub_dir = Path(orig_docs_sub_dir)
        source_path = orig_docs_dir / orig_docs_sub_dir
        for item in source_path.rglob("*"):
            destination_path = Path(self.merged_docs_dir) / source_path.name / item.relative_to(source_path)
            print(self.merged_docs_dir, source_path.name, item.relative_to(source_path))

            if item.is_file():
                # Skip the nav.yaml file
                if item.name == "nav.yml" or item.name == "nav.yaml":
                    continue
            
                # Check if the file already exists in the destination
                if destination_path.exists():
                    log.error(f"Duplicate file: {item} already exists in the destination directory. Skipping.")
                    continue
                    
                # Make sure the destination directory exists
                destination_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file to the destination path
                shutil.copy2(item, destination_path)

                # Store the source directory for the copied file
                self.files_source_dir[str(destination_path)] = { "parent": str(item.parent),
                                                                "file": str(item.name),
                                                                "orig_path": str(source_path),
                                                                "edit_path": "" }
            elif item.is_dir():
                # Make sure the destination directory exists
                destination_path.mkdir(parents=True, exist_ok=True)

    def merge(self, additional_info):
        # Copy original docs
        self._copy_original()

        # Copy the rest
        for item in additional_info:
            orig_docs_dir = item.get("orig_docs_dir")
            orig_docs_sub_dir = item.get("orig_docs_sub_dir")
            self._append(orig_docs_dir, orig_docs_sub_dir)
        return self.files_source_dir, self.merged_docs_dir
