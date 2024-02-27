#!/usr/bin/python3
# -*- coding: utf-8 -*-

##############################################################################
#
#    Odoo Proprietary License v1.0
#
#    Copyright (c) 2013 LogicaSoft SPRL (<http://www.logicasoft.eu>).
#
#    This software and associated files (the "Software") may only be used (executed,
#    modified, executed after modifications) if you have purchased a valid license
#    from the authors, typically via Odoo Apps, or if you have received a written
#    agreement from the authors of the Software.
#
#    You may develop Odoo modules that use the Software as a library (typically
#    by depending on it, importing it and using its resources), but without copying
#    any source code or material from the Software. You may distribute those
#    modules under the license of your choice, provided that this license is
#    compatible with the terms of the Odoo Proprietary License (For example:
#    LGPL, MIT, or proprietary licenses similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
##############################################################################

import os
import sys
import re
from pathlib import PosixPath as Path
import argparse
from subprocess import Popen, DEVNULL, PIPE
from itertools import groupby
from pprint import pprint as ppr
from functools import partial
import itertools as it
import glob
from ast import literal_eval
from distutils.version import LooseVersion as Version


# github doesn't care about stderr:
old_stderr = sys.stderr
sys.stderr = sys.stdout

VERSION_PATTERN = r"""^([+-]).*['"]version['"]\s*:\s*['"]([\d.]+)['"]"""
SCRIPT_ERROR = 1
CMD_ERROR = 3
GIT_ERROR = 4
EXIT_VERSION_NOT_INCREMENTED = 8
EXIT_MORE_THAN_ONE_REPO = 9


def _exec_cmd(cmd, error_code):
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    if err:
        msg = "error: {}\ncommand: {}\n".format(
            err.decode(),
            cmd)
        sys.stderr.write(msg)
        sys.exit(error_code)
    else:
        return out.decode()


def exec_cmd(cmd):
    if cmd.startswith('git'):
        error_code = GIT_ERROR
    else:
        error_code = CMD_ERROR
    return _exec_cmd(cmd, error_code=error_code)


def git_url(path):
    return exec_cmd(f"""git -C "{path}" remote get-url --push origin""").strip()


class File():
    def __init__(self, path, status=None, module=False, init=None):
        self.path = Path(path)
        self.name = self.path.name
        self.parent = self.path.parent
        self.status = status
        self.status_text = {
            'A': "Added",
            'C': "Copied",
            'M': "Modified",
            'D': "Deleted",
            'R': "Renamed",
            'T': "Type changed",
            'U': "Unmerged",
            'X': "Unknown",
        }.get(self.status)
        if not init and module is False:
            raise Exception("You should provide a module if not in init mode")
        self.module = module

    def __str__(self):
        return f"{self.path} [status: {self.status}]"

    def __repr__(self):
        return self.__str__()


class Module():
    def __init__(self, path, repository):
        self.name = path.name
        self.path = path
        self.repository = repository
        self.manifest_path = self.get_manifest()

    def get_manifest(self):
        def multiple_file_types(patterns):
            return it.chain.from_iterable(self.path.glob(pattern) for pattern in patterns)
        return next(multiple_file_types(['__manifest__.py', '__openerp__.py', '__terp__.py']))

    def __str__(self):
        return f"{self.name} [path: {self.path}, repository: {self.repository}]"

    def __repr__(self):
        return self.__str__()


class Manifest():
    def __init__(self, path):
        self.name = path.parent.name
        self.path = path
        self.content = self.evaluate_content()

    def evaluate_content(self):
        return literal_eval(open(self.path, 'r').read())

    def __str__(self):
        return f"{self.name} [path: {self.path}"

    def __repr__(self):
        return self.__str__()


class Repository():
    def __init__(self, path):
        self.path = path
        self.url = git_url(path)
        self.is_submodule = bool(self.git_is_submodule(path))

    def git_is_submodule(self, path):
        cmd = f"""git -C "{path}" rev-parse --show-superproject-working-tree"""
        return exec_cmd(cmd)

    def __str__(self):
        return f"{self.url} [path: {self.path}, is_submodule: {self.is_submodule}]"

    def __repr__(self):
        return self.__str__()


class CommitChecker():
    def __init__(self, args):
        self.args = args
        self.verbose = self._get_verbosity()
        self.files_by_ext = {}
        self.posixfiles_by_path = {}
        self.all_files = []
        self.deleted_files = []
        self.modified_files = []
        self.repositories = []
        self.manifests = []
        self.modules = []

        self.init()

    def _get_verbosity(self):
        return self.args.verbose and sum(self.args.verbose) or 0

    def log(self, msg, verbosity=1):
        if self.verbose >= verbosity:
            sys.stderr.write(msg+'\n')
            sys.stderr.flush()

    def init(self):
        self.all_files = self.get_all_files()

        # repositories:
        self.repositories += self.get_repositories()

        # modules:
        for f in self.all_files:
            if self.is_manifest(f):
                self.manifests += [Manifest(f.path)]
                r1 = [r for r in self.repositories if str(r.path).startswith(str(f.parent.parent)+'/')]
                if len(r1) > 1:
                    msg = f"There should only be one non-submodule repository. There are {len(r1)}\n"
                    sys.stderr.write(msg)
                    sys.exit(EXIT_MORE_THAN_ONE_REPO)
                if not r1:
                    r1 = [r for r in self.repositories if not r.is_submodule]
                elif len(r1) > 1:
                    raise Exception("Repository should be 1")

                if r1:
                    mod = Module(f.parent, r1[0])
                    self.modules += [mod]

        # assign module to files:
        for f in self.all_files:
            modules = [m for m in self.modules if str(f.path).startswith(str(m.path)+'/')]
            f.module = modules[0] if modules else None

        # files by extentions:
        self.files_by_ext = self._group_files_by_ext(self.all_files)

        # files by path:
        self.posixfiles_by_path = self._group_files_by_path(self.all_files)

        # modified files:
        self.deleted_files, self.modified_files = self.get_modified_files()

    def get_repositories(self):
        repositories = []
        out = exec_cmd("find -iname '.git'")
        for git_file in out.splitlines():
            repo = Repository(Path(git_file).parent)
            repositories.append(repo)
        return repositories

    def get_all_files(self):
        out = exec_cmd("git ls-tree --full-tree -r --name-only HEAD")
        files = [
            File(f, init=True) for f
            in out.splitlines()
            if not f.endswith(('.pyc', '.pyo'))
        ]
        return files

    def get_modified_files(self):
        out = exec_cmd("git diff-tree --no-commit-id --name-status -r HEAD")
        deleted_files, modified_files = [], []
        for modified_file in out.splitlines():
            status, filename = modified_file.split('\t')
            if Path(filename).is_dir():
                continue

            if status == 'D':
                mod = os.path.split(filename)[0]
                modules = [m for m in self.modules if mod.startswith(str(m.path)+'/')] or None
                if modules:
                    module = modules[0]
                    f = File(filename, status, module=module)
                else:
                    f = File(filename, status, init=True)
                deleted_files.append(f)
            else:
                f = self.posixfiles_by_path[filename]
                f.status = status
                modified_files.append(f)
        return deleted_files, modified_files

    def _group_files_by_ext(self, file_list):
        def ext_func(f):
            return os.path.splitext(f.path)[-1].lower()[1:]
        return {
            k: list(itr)
            for k, itr in
            groupby(sorted(file_list, key=lambda f: ext_func(f)), lambda f: ext_func(f))
        }

    def _group_files_by_path(self, file_list):
        return {str(k.path): k for k in file_list}

    def is_manifest(self, path):
        return path.name.endswith(('__manifest__.py', '__openerp__.py', '__terp__.py'))

    def evaluate_manifest(self, path):
        if self.is_manifest(path):
            return literal_eval(open(path, 'r'))
        else:
            raise Exception(f"Not a manifest file: {path}")

    def manifest_files(self, files):
        def filterfunc(item, patterns):
            return any(pattern in item for pattern in patterns)
        manifest_patterns = ['__manifest__.py', '__openerp__.py', '__terp__.py']
        return list(filter(partial(filterfunc, patterns=manifest_patterns), files))

    def check_manifest(self):
        last_commit = exec_cmd("git describe --always --tags --long --first-parent").strip()
        modified_by_modules = {}
        for f in self.modified_files + self.deleted_files:
            if not f.module:
                continue

            modified_by_modules.setdefault(
                f.module.name,
                {
                    'to_check': True,
                    'files': [],
                })
            modified_by_modules[f.module.name]['files'].append(f)
            if self.is_manifest(f) and f.status == 'A':
                # module is new -> no check on version
                modified_by_modules[f.module.name]['to_check'] = False

        errors = {}
        for mod_def in modified_by_modules.values():
            if not mod_def['to_check']:
                continue

            for modified in mod_def['files']:
                if not modified.module:
                    continue

                error = False
                diff = exec_cmd(
                    f"""git diff --unified=0 '{last_commit}^..{last_commit}' {modified.module.manifest_path}"""
                )
                version_lines = re.findall(VERSION_PATTERN, diff, re.MULTILINE)

                if not version_lines:
                    error = True
                else:
                    version_error = False
                    try:
                        version_diff = {k: Version(v) for k, v in version_lines}
                    except Exception as exc:
                        sys.stderr.write(str(exc)+'\n')
                        sys.exit(SCRIPT_ERROR)

                    if '-' not in version_diff:
                        version_error = True
                    elif '+' not in version_diff:
                        version_error = True
                    elif version_diff['-'] >= version_diff['+']:
                        version_error = True
                    if version_error:
                        error = True
                if error:
                    msg = f"Version not incremented in manifest\n  module: {modified.module.name}\n"
                    errors[modified.module.name] = msg

            if errors:
                for _, msg in errors.items():
                    sys.stderr.write(msg)
                sys.exit(EXIT_VERSION_NOT_INCREMENTED)

    def run(self):
        self.check_manifest()


def main(args):
    app = CommitChecker(args)
    app.run()


parser = argparse.ArgumentParser()
parser.add_argument('path', help="Path to git sources")
parser.add_argument('-v', '--verbose', help="Verbose output")
args = parser.parse_args()

main(args)

