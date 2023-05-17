import errno
import logging
import os
import shutil
import sys
from tempfile import mkdtemp

import git
from mkdocs.utils import warning_filter

log = logging.getLogger(__name__)
log.addFilter(warning_filter)


class GitClone:
    def __init__(self, target_dir=None):
        """
        Initialize GitClone object.

        :param target_dir: The target directory where the git repositories will be cloned.
        """
        self.target_dir = target_dir or mkdtemp()

        if not target_dir is None:
            if not os.path.exists(target_dir):
                try:
                    os.makedirs(target_dir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        log.error(
                            f"Error creating target directory '{target_dir}': {e}",
                            file=sys.stderr)
                        self.cleanup()
                        raise SystemExit(1)

    def _is_git_repo(self, path):
        """
        Check if a given path contains a .git directory.

        :param path: The path to check.
        :return: True if .git directory is present, False otherwise.
        """
        if not os.path.exists(path):
            return False

        try:
            repo = git.Repo(path)
            return os.path.samefile(repo.git.rev_parse("--show-toplevel"),
                                    self.target_dir)
        except git.InvalidGitRepositoryError:
            return False

    # TODO: Improve the error handling by allowing the cloning to fail and instead omitting the `!include` string from the nav.
    def clone(self, git_url, git_ref="main"):
        """
        Clone a git repository into the specified target directory.

        :param git_url: The URL of the git repository to clone.
        :param git_ref: The git reference to checkout after cloning (default: "main").
        :return: The target directory where the repository was cloned.
        """
        try:
            repo_name = os.path.splitext(os.path.basename(git_url))[0]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]

            if self.target_dir is None:
                self.target_dir = os.path.join(self.tempdir,
                                               os.path.basename(repo_name))
            else:
                self.target_dir = os.path.join(self.target_dir,
                                               os.path.basename(repo_name))

            if not self._is_git_repo(self.target_dir):
                repo = git.Repo.clone_from(git_url, self.target_dir)
                repo.git.checkout(git_ref)
            else:
                log.info(
                    f"The repository '{git_url}' is already cloned at '{self.target_dir}'."
                )
                repo = git.Repo(self.target_dir)
                repo.git.checkout(git_ref)

            return self.target_dir
        except git.GitCommandError as e:
            log.error(
                f"Error while cloning the repository '{git_url}': {e.stderr.strip()}",
                file=sys.stderr)
            raise SystemExit(1)
        except Exception as e:
            log.error(
                f"Unexpected error while cloning the repository '{git_url}': {e}",
                file=sys.stderr)
            raise SystemExit(1)

    def cleanup(self):
        try:
            shutil.rmtree(self.tempdir)
            log.debug(f"Temporary directory '{self.tempdir}' has been cleaned up.")
        except FileNotFoundError as e:
            log.error(f"Error while cleaning up the temporary directory: {e}",
                  file=sys.stderr)
        except Exception as e:
            log.error(
                f"Unexpected error while cleaning up the temporary directory: {e}",
                file=sys.stderr)
