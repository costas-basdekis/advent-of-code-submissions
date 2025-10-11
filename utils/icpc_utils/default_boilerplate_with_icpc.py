import re
from pathlib import Path
from typing import Tuple, Optional, List

from aox.boilerplate import DefaultBoilerplate
from aox.settings import settings_proxy
from aox.utils import get_current_directory


__all__ = ['DefaultBoilerplateWithIcpc']

current_directory = get_current_directory()


class DefaultBoilerplateWithIcpc(DefaultBoilerplate):
    re_icpc_filename = re.compile(r"^(?:.*/)?icpc/year_(\d+)/problem_(\w).py$")

    example_icpc_year_path: Path = current_directory\
        .joinpath('default_boilerplate_example_year')
    example_icpc_day_path: Path = example_icpc_year_path.joinpath('example_day')
    example_icpc_part_path: Path = current_directory / ''

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

    def get_icpc_problem_file_pair(self, year: int, problem: str, input_name: str, relative: bool = False) -> Tuple[Path, Path]:
        return (
            self.get_icpc_problem_file(year, problem, input_name, relative=relative),
            self.get_icpc_output_file(year, problem, input_name, relative=relative),
        )

    def get_icpc_problem_file(self, year: int, problem: str, input_name: str, relative: bool = False) -> Path:
        data_directory = self.get_icpc_problem_data_directory(year, problem, relative=relative)
        input_file = data_directory / f"{input_name}.in"
        if not input_file.exists():
            raise FileNotFoundError(f"Could not find input file {input_file}")
        return input_file

    def get_icpc_output_file(self, year: int, problem: str, input_name: str, relative: bool = False) -> Path:
        data_directory = self.get_icpc_problem_data_directory(year, problem, relative=relative)
        input_file = data_directory / f"{input_name}.ans"
        if not input_file.exists():
            raise FileNotFoundError(f"Could not find output file {input_file}")
        return input_file

    def get_icpc_problem_data_directory(self, year: int, problem: str, relative: bool = False) -> Path:
        """
        >>> str(DefaultBoilerplateWithIcpc().get_icpc_problem_data_directory(2025, "a", True))
        'icpc/year_2025/data/A-askewedreasoning'
        """
        if relative:
            base = Path()
        else:
            base = settings_proxy().challenges_root
        if base is None:
            raise FileNotFoundError(f"No base given")
        data_dir = base / "icpc" / f"year_{year}" / "data"
        if not data_dir.exists():
            raise FileNotFoundError(f"Year data directory {data_dir} does not exist")
        paths = list(data_dir.glob(f"{problem.upper()}-*"))
        if not paths:
            raise FileNotFoundError(f"Problem data directory {data_dir}/A-* does not exist")
        return paths[0]
