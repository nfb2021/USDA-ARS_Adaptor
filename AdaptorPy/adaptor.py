import os
from glob import iglob
from typing import Optional, Any
from tqdm import trange


class Adaptor:

    """Small class dealing with inconsistent file names and header of USDA-ARS data in the "header and values" format of the ISMN database.
    This class is not intended for other manipulations, but can serve as starting point for such.
    :param database_name: The name of the database
    :type database_name: str
    :param pattern: The name of the Network, which files will be adapted. Per default network "USDA-ARS"
    :type pattern: Optional [str]"""

    def __init__(self, database_name: str, pattern: Optional[str] = "USDA-ARS") -> None:
        self.database_name: str = database_name
        self.root: str = os.getcwd()
        self.database_path: str = os.path.join(self.root, self.database_name)
        self.pattern: str = pattern

    def check_for_pattern(self) -> Any:
        """Check if the specified network exists.
        :return: True if the specified network exists, otherwise raises an exception"""
        if os.path.isdir(os.path.join(self.database_path, self.pattern)):
            self.destination: str = os.path.join(self.database_path, self.pattern)
            return True
        else:
            print(
                f'\n\tThe specified network "{self.pattern}" does not exist in the database "{self.database_name}".\n'
            )
            exit(1)

    def get_stm_files(self) -> list:
        """Returns a list of all stm files."""
        if self.check_for_pattern():
            os.chdir(self.destination)

            return [
                f
                for f in iglob(
                    os.path.join(self.destination, "*", "**"), recursive=True
                )
                if os.path.isfile(f) and f.endswith(".stm")
            ]

    def adapt_files(self) -> None:
        """Renames the files and adapts the header"""
        stm_files = self.get_stm_files()
        for s in trange(len(stm_files), desc="Iterating over .stm files"):
            stm = stm_files[s]
            splitted = stm.split("(2.5-Volt)---")
            try:
                new = f"{splitted[0]}2500-mV-{splitted[1]}"

                with open(stm) as f_in:
                    lines = [line for line in f_in]

                with open(new, "w") as f_out:
                    for ll, line in enumerate(lines):
                        if ll == 0:
                            line_split = line.split(" (2.5 Volt) - ")
                            new_header = f'{line_split[0]} 2500 mV {"_".join(line_split[1].split(" "))}'
                            f_out.write(new_header)
                        else:
                            f_out.write(line)

                os.remove(stm)

            except IndexError:
                print(
                    f'\n\tThe adaptions were not applied to file "{stm}".\n\tMaybe the intended adaptions were already implemented? \
                    \n\tPlease pay attention to this.\n'
                )
