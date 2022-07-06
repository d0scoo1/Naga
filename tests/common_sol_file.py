"""
Etherscan platform.
"""

import json
import logging
import os
import re
import urllib.request
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Union, Tuple, Optional

from crytic_compile.compilation_unit import CompilationUnit
from crytic_compile.compiler.compiler import CompilerVersion
from crytic_compile.platform import solc_standard_json
from crytic_compile.platform.abstract_platform import AbstractPlatform
from crytic_compile.platform.exceptions import InvalidCompilation
from crytic_compile.platform.types import Type
from crytic_compile.utils.naming import Filename

# Cycle dependency

if TYPE_CHECKING:
    from crytic_compile import CryticCompile

#LOGGER = logging.getLogger("CryticCompile")


def _get_multiple_files(
    working_dir: str,
) -> Tuple[List[str], str]:
    """Handle a result with a multiple files. Generate multiple Solidity files

    Args:
        working_dir

    Returns:
        Tuple[List[str], str]: filesnames, directory, where target_filename is the main file
    """
    if working_dir.endswith('/'):
        working_dir = working_dir[:-1]
    
    prefix_len = len(working_dir) + 1

    sol_files = []
    for root, dirs, files in os.walk(working_dir):
        for file in files:
            if file.endswith('.sol'):
                sol_files.append(os.path.join(root, file)[prefix_len:])
    

    return sol_files, working_dir


class CommonSolFile(AbstractPlatform):
    """
    single file or multiple files
    """

    NAME = "CommonSolFile"
    PROJECT_URL = "https://dos.cool"
    TYPE = Type.SOLC_STANDARD_JSON

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def compile(self, crytic_compile: "CryticCompile", **kwargs: str) -> None:
        """Run the compilation

        Args:
            crytic_compile (CryticCompile): Associated CryticCompile object
            **kwargs: optional arguments. Used "solc", 
            "contract_name"

        Raises:
            InvalidCompilation: if etherscan returned an error, or its results were not correctly parsed
        """

        target = self._target #"sol_file" or "sol_dir"
        if target.endswith('.sol'):
            filenames = [target]
            working_dir = None
        else:
            filenames, working_dir = _get_multiple_files(target)

        contract_name = kwargs.get("contract_name", None)
        compiler_version = kwargs.get("compiler_version", None)
        optimization_used = kwargs.get("optimization_used", False)
        #optimize_runs = kwargs.get("optimize_runs", None)
        
        compilation_unit = CompilationUnit(crytic_compile, contract_name)

        compilation_unit.compiler_version = CompilerVersion(
            compiler=kwargs.get("solc", "solc"),
            version=compiler_version,
            optimized=optimization_used,
            #optimize_runs=optimize_runs,
        )
        #compilation_unit.compiler_version.look_for_installed_version()

        solc_standard_json.standalone_compile(filenames, compilation_unit, working_dir=working_dir)

    @staticmethod
    def is_supported(target: str, **kwargs: str) -> bool:
        """Check if the target is a etherscan project

        Args:
            target (str): path to the target
            **kwargs: optional arguments. Used "etherscan_ignore"

        Returns:
            bool: True if the target is a etherscan project
        """
        return False

    def is_dependency(self, _path: str) -> bool:
        """Check if the path is a dependency

        Args:
            _path (str): path to the target

        Returns:
            bool: True if the target is a dependency
        """
        return False

    def _guessed_tests(self) -> List[str]:
        """Guess the potential unit tests commands

        Returns:
            List[str]: The guessed unit tests commands
        """
        return []
