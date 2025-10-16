import re
from pathlib import Path
from typing import Tuple, Optional, List

from aox.boilerplate import DefaultBoilerplate
from aox.settings import settings_proxy
from aox.styling.shortcuts import e_value, e_warn
import click
import shutil


__all__ = ['DefaultBoilerplateWithIcpc']


class DefaultBoilerplateWithIcpc(DefaultBoilerplate):
    re_icpc_filename = re.compile(r"^(?:.*/)?icpc/year_(\d+)/problem_(\w).py$")

    def extract_from_filename(self, filename: str) -> Tuple[int, int, str]:
        parts = self.extract_icpc_from_filename(filename)
        if parts is None:
            return super().extract_from_filename(filename)
        year, part = parts
        return year, 1, part

    def extract_icpc_from_filename(self, filename: str) -> Optional[Tuple[int, str]]:
        """
        >>> DefaultBoilerplateWithIcpc().extract_icpc_from_filename(
        ...     '/home/user/git/my-aoc/icpc/year_2020/problem_d.py')
        (2020, 'd')
        """
        match = self.re_icpc_filename.match(filename)
        if not match:
            return None
        year_str, part_str = match.groups()
        return int(year_str), part_str

    def get_icpc_sample_problem_file(self, year: int, problem: str, relative: bool = False) -> Optional[Path]:
        data_directory = self.get_icpc_problem_data_directory(year, problem, relative=relative)
        sample = data_directory / "sample-1.in"
        if sample.exists():
            return sample
        input_files = data_directory.glob("*.in")
        for sample in input_files:
            return sample
        raise FileNotFoundError(f"Could not find an input file in {data_directory}")

    def get_icpc_problem_file_names(self, year: int, problem: str, relative: bool = False) -> List[str]:
        data_directory = self.get_icpc_problem_data_directory(year, problem, relative=relative)
        input_files = list(data_directory.glob("*.in"))
        return [
            input_file.name[:-3]
            for input_file in input_files
        ]

    def get_icpc_problem_file_pair(self, year: int, problem: str, input_name: str, relative: bool = False, partial_match: bool = False) -> Tuple[Path, Path]:
        input_file = self.get_icpc_problem_file(year, problem, input_name, relative=relative, partial_match=partial_match)
        actual_input_name = input_file.name[:-len(".in")]
        return (
            input_file,
            self.get_icpc_output_file(year, problem, actual_input_name, relative=relative),
        )

    def get_icpc_problem_files(self, year: int, problem: str, input_name: str, relative: bool = False, partial_match: bool = False) -> List[Path]:
        data_directory = self.get_icpc_problem_data_directory(year, problem, relative=relative)
        input_file = data_directory / f"{input_name}.in"
        if not input_file.exists():
            if partial_match:
                return list(data_directory.glob(f"*{input_name}*.in"))
            return []
        return [input_file]

    def get_icpc_problem_file(self, year: int, problem: str, input_name: str, relative: bool = False, partial_match: bool = False) -> Path:
        input_files = self.get_icpc_problem_files(year, problem, input_name, relative=relative, partial_match=partial_match)
        if not input_files:
            data_directory = self.get_icpc_problem_data_directory(year, problem, relative=relative)
            input_file = data_directory / f"{input_name}.in"
            raise FileNotFoundError(f"Could not find input file {input_file}")
        if len(input_files) > 1:
            data_directory = self.get_icpc_problem_data_directory(year, problem, relative=relative)
            input_file = data_directory / f"{input_name}.in"
            raise FileNotFoundError(
                f"Could not find input file {input_file}, "
                f"and there are {len(input_files)} files with that prefix: "
                f"{', '.join(possible_file.name for possible_file in input_files)}")
        input_file, = input_files
        return input_file

    def get_icpc_output_file(self, year: int, problem: str, input_name: str, relative: bool = False) -> Path:
        data_directory = self.get_icpc_problem_data_directory(year, problem, relative=relative)
        input_file = data_directory / f"{input_name}.ans"
        if not input_file.exists():
            raise FileNotFoundError(f"Could not find output file {input_file}")
        return input_file
    
    def get_icpc_year_directory(self, year: int, relative: bool = False) -> Path:
        if relative:
            base = Path()
        else:
            base = settings_proxy().challenges_root
        if base is None:
            raise FileNotFoundError(f"No base given")
        return base / "icpc" / f"year_{year}"

    def get_icpc_problem_data_directory(self, year: int, problem: str, relative: bool = False) -> Path:
        """
        >>> str(DefaultBoilerplateWithIcpc().get_icpc_problem_data_directory(2025, "a", True))
        'icpc/year_2025/data/A-askewedreasoning'
        """
        data_dir = self.get_icpc_year_directory(year, relative=relative) / "data"
        if not data_dir.exists():
            raise FileNotFoundError(f"Year data directory {data_dir} does not exist")
        paths = list(data_dir.glob(f"{problem.upper()}-*"))
        if not paths:
            raise FileNotFoundError(f"Problem data directory {data_dir}/A-* does not exist")
        return paths[0]

    def create_icpc_part(self, year: int, part: str) -> Optional[Path]:
        year_path = self.get_icpc_year_directory(year)
        problem_path = year_path / f"problem_{part}.py"

        if problem_path.exists():
            click.echo(
                f"Challenge {e_warn(f'{year} {part.upper()}')} already "
                f"exists at {e_value(str(problem_path))}")
            return None

        year_init_path = year_path / "__init__.py"
        if not year_init_path.exists():
            year_init_path.parent.mkdir(exist_ok=True)
            year_init_path.touch()
        example_problem_path = settings_proxy().challenges_root / "custom" / "custom_icpc_example_problem.py"
        shutil.copy(example_problem_path, problem_path)
        return problem_path
