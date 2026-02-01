"""
Test fixtures for benchmark suite.

This module provides utilities for generating synthetic codebases
of varying sizes (10, 100, 1000 files) for performance testing.
"""

import os
import random
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Common Python code templates
FUNCTION_TEMPLATES = [
    """def {name}({params}):
    \"\"\"
    {docstring}
    \"\"\"
    {body}
    return {return_value}
""",
    """def {name}({params}):
    {body}
""",
    """async def {name}({params}):
    \"\"\"
    {docstring}
    \"\"\"
    {body}
    return {return_value}
""",
]

CLASS_TEMPLATES = [
    """class {name}:
    \"\"\"
    {docstring}
    \"\"\"

    def __init__(self{params}):
        {init_body}

    {methods}
""",
    """class {name}({base_class}):
    \"\"\"
    {docstring}
    \"\"\"

    {methods}
""",
]


def generate_function_name() -> str:
    """Generate a random function name."""
    verbs = ["process", "handle", "calculate", "validate", "transform", "parse", "format"]
    nouns = ["data", "input", "value", "result", "config", "request", "response"]
    return f"{random.choice(verbs)}_{random.choice(nouns)}"


def generate_class_name() -> str:
    """Generate a random class name."""
    prefixes = ["Base", "Abstract", "Simple", "Advanced", "Custom"]
    suffixes = ["Manager", "Handler", "Processor", "Controller", "Service", "Utility"]
    return f"{random.choice(prefixes)}{random.choice(suffixes)}"


def generate_variable_name() -> str:
    """Generate a random variable name."""
    names = ["data", "value", "result", "config", "item", "entry", "record", "element"]
    return random.choice(names)


def generate_function(include_docstring: bool = True) -> str:
    """
    Generate a random Python function.

    Args:
        include_docstring: Whether to include a docstring.

    Returns:
        A string containing a Python function definition.
    """
    template = random.choice(FUNCTION_TEMPLATES)
    name = generate_function_name()

    # Generate parameters
    param_count = random.randint(0, 3)
    params = ", ".join([generate_variable_name() for _ in range(param_count)])

    # Generate body
    body_lines = []
    for _ in range(random.randint(1, 5)):
        var = generate_variable_name()
        body_lines.append(f"    {var} = None")
    body = "\n    ".join(body_lines) if body_lines else "pass"

    # Fill template
    return template.format(
        name=name,
        params=params,
        docstring=f"Process and return {generate_variable_name()}." if include_docstring else "",
        body=body,
        return_value=generate_variable_name()
    )


def generate_class(include_methods: bool = True) -> str:
    """
    Generate a random Python class.

    Args:
        include_methods: Whether to include methods.

    Returns:
        A string containing a Python class definition.
    """
    name = generate_class_name()

    # Generate methods
    methods = []
    if include_methods:
        method_count = random.randint(1, 4)
        for _ in range(method_count):
            methods.append(generate_function(include_docstring=False))

    methods_str = "\n    ".join(methods) if methods else "pass"

    # Generate init body
    init_vars = []
    for _ in range(random.randint(1, 3)):
        var = generate_variable_name()
        init_vars.append(f"self.{var} = {var}")
    init_body = "\n        ".join(init_vars) if init_vars else "pass"

    template = random.choice(CLASS_TEMPLATES)

    # Handle template variations
    if "{base_class}" in template:
        base_classes = ["object", "BaseClass", "AbstractBase"]
        return template.format(
            name=name,
            base_class=random.choice(base_classes),
            docstring=f"{name} implementation.",
            methods=methods_str
        )
    else:
        # Generate parameters for __init__
        param_count = random.randint(1, 3)
        params = ", " + ", ".join([generate_variable_name() for _ in range(param_count)])

        return template.format(
            name=name,
            params=params,
            docstring=f"{name} implementation.",
            init_body=init_body,
            methods=methods_str
        )


def generate_python_file(
    file_path: str,
    num_functions: int = 3,
    num_classes: int = 2,
    include_imports: bool = True,
    related_files: Optional[List[str]] = None
) -> str:
    """
    Generate a synthetic Python file with functions and classes.

    Args:
        file_path: Path where the file will be created.
        num_functions: Number of functions to generate.
        num_classes: Number of classes to generate.
        include_imports: Whether to include import statements.
        related_files: List of related file paths to import from.

    Returns:
        The generated file content as a string.
    """
    lines = []

    # Add docstring
    module_name = Path(file_path).stem
    lines.append(f'"""')
    lines.append(f'{module_name} module.')
    lines.append('')
    lines.append(f'This module provides functionality for {generate_variable_name()} processing.')
    lines.append(f'"""')
    lines.append('')

    # Add imports
    if include_imports:
        standard_imports = [
            "import os",
            "import sys",
            "from typing import Any, Dict, List, Optional",
            "from pathlib import Path",
        ]
        lines.extend(random.sample(standard_imports, k=random.randint(1, 3)))
        lines.append('')

        # Add imports from related files
        if related_files:
            for rel_file in random.sample(related_files, k=min(3, len(related_files))):
                module = Path(rel_file).stem
                class_name = generate_class_name()
                lines.append(f"from {module} import {class_name}")
            lines.append('')

    # Add constants
    lines.append(f"DEFAULT_{generate_variable_name().upper()} = None")
    lines.append(f"MAX_{generate_variable_name().upper()} = 100")
    lines.append('')

    # Add functions
    for _ in range(num_functions):
        lines.append(generate_function())
        lines.append('')

    # Add classes
    for _ in range(num_classes):
        lines.append(generate_class())
        lines.append('')

    return '\n'.join(lines)


def generate_file_with_imports(
    file_path: str,
    import_files: List[str]
) -> str:
    """
    Generate a Python file that imports from specified files.

    This is useful for creating files with explicit dependencies
    for testing relationship tracking.

    Args:
        file_path: Path where the file will be created.
        import_files: List of file paths to import from.

    Returns:
        The generated file content as a string.
    """
    lines = []

    # Add docstring
    module_name = Path(file_path).stem
    lines.append(f'"""')
    lines.append(f'{module_name} module with dependencies.')
    lines.append(f'"""')
    lines.append('')

    # Add imports from specified files
    for import_file in import_files:
        module = Path(import_file).stem
        class_name = generate_class_name()
        lines.append(f"from {module} import {class_name}")
    lines.append('')

    # Add some content
    lines.append(generate_function())
    lines.append('')
    lines.append(generate_class())

    return '\n'.join(lines)


def generate_test_codebase(
    size: int = 10,
    include_relationships: bool = True,
    temp_dir: Optional[str] = None
) -> Tuple[str, List[str], Dict[str, List[str]]]:
    """
    Generate a synthetic Python codebase with multiple files.

    This function creates a temporary directory structure with Python files
    of varying complexity. The files can optionally include import relationships
    to simulate a real codebase structure.

    Args:
        size: Number of files to generate (10, 100, 1000, etc.).
        include_relationships: Whether to create import relationships between files.
        temp_dir: Optional directory to use. If None, creates a temporary directory.

    Returns:
        A tuple containing:
        - base_dir: Path to the directory containing generated files.
        - file_paths: List of absolute paths to all generated files.
        - relationships: Dictionary mapping file paths to their imported files.

    Example:
        >>> base_dir, files, rels = generate_test_codebase(size=10)
        >>> len(files)
        10
        >>> all(os.path.exists(f) for f in files)
        True
    """
    if temp_dir is None:
        base_dir = tempfile.mkdtemp(prefix="benchmark_codebase_")
    else:
        base_dir = temp_dir
        os.makedirs(base_dir, exist_ok=True)

    file_paths = []
    relationships = {}

    # Generate directory structure
    # For larger codebases, create a hierarchy
    if size <= 10:
        subdirs = [""]
    elif size <= 100:
        subdirs = ["", "utils", "core", "services"]
    else:
        subdirs = ["", "utils", "core", "services", "models", "handlers", "api", "db"]

    # Create subdirectories
    for subdir in subdirs:
        if subdir:
            os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)
            # Create __init__.py for each package
            init_path = os.path.join(base_dir, subdir, "__init__.py")
            with open(init_path, "w") as f:
                f.write(f'"""{subdir} package."""\n')

    # Generate files
    files_per_dir = size // len(subdirs) + 1
    file_count = 0

    for subdir in subdirs:
        for i in range(files_per_dir):
            if file_count >= size:
                break

            # Generate filename
            prefix = random.choice(["manager", "handler", "processor", "service", "util", "model"])
            filename = f"{prefix}_{i}.py"

            if subdir:
                file_path = os.path.join(base_dir, subdir, filename)
            else:
                file_path = os.path.join(base_dir, filename)

            # Determine related files for imports
            related_files = []
            if include_relationships and file_paths:
                # Randomly select some existing files to import from
                num_imports = random.randint(0, min(3, len(file_paths)))
                related_files = random.sample(file_paths, k=num_imports)
                relationships[file_path] = related_files

            # Generate file content
            content = generate_python_file(
                file_path,
                num_functions=random.randint(2, 5),
                num_classes=random.randint(1, 3),
                include_imports=True,
                related_files=related_files
            )

            # Write file
            with open(file_path, "w") as f:
                f.write(content)

            file_paths.append(file_path)
            file_count += 1

        if file_count >= size:
            break

    return base_dir, file_paths, relationships
