"""

    Project Typing Extensions
    @gl36
    
    20/06/2025

"""

# Imports
import typing
import dataclasses

# Types

@dataclasses.dataclass
class Project:
    # Classes
    @dataclasses.dataclass
    class Repository:
        owner: str
        name: str

    @dataclasses.dataclass
    class ProjectInformation:
        name: str
        app_id: str

    # Actual type

    repository: Repository
    project_information: ProjectInformation
