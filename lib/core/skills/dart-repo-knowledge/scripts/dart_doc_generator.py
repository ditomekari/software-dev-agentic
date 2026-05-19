"""DartDoc JSON generation from Dart source files.

This module provides the DartDocGenerator class which handles:
- Parallel processing of Dart files using dartdoc_json
- Filtering out files without useful documentation
- Versioned output directory support

Example:
    from src import DartDocGenerator

    output_dir = DartDocGenerator.generate_json(
        source_dir="lib",
        output_dir="dataset",
        version="v1.0.0",
        workers=4
    )
"""

import os
import json
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def _process_file(
    file: str,
    file_path: str,
    output_dir: str,
    lock: threading.Lock,
) -> bool:
    """Process a single Dart file: allocate output path,
    run dartdoc_json, validate and prune empty output.

    Args:
        file: Dart filename (basename only).
        file_path: Absolute path to the Dart source file.
        output_dir: Directory to write the JSON output.
        lock: Shared lock that protects the filename
            allocation block against race conditions
            when multiple threads check/create the same
            output path simultaneously.

    Returns:
        True if a useful JSON file was produced,
        False if output was empty/invalid.
    """
    base_name = os.path.splitext(file)[0]

    # Allocate a unique output path under the lock to
    # prevent two threads writing to the same filename.
    with lock:
        output_file = os.path.join(
            output_dir, f"{base_name}.json"
        )
        counter = 1
        while os.path.exists(output_file):
            output_file = os.path.join(
                output_dir,
                f"{base_name}_{counter}.json",
            )
            counter += 1
        # Create a placeholder so no other thread steals
        # this path before the subprocess writes to it.
        open(output_file, 'w').close()

    # Run dartdoc_json outside the lock — this is the
    # expensive part and is fully independent per file.
    result = subprocess.run(
        [
            "dartdoc_json", file_path,
            "--output", output_file,
            "--pretty",
        ],
        capture_output=True,
    )

    if result.returncode != 0 or not os.path.exists(
        output_file
    ):
        # Remove placeholder if subprocess failed
        if os.path.exists(output_file):
            os.remove(output_file)
        return False

    # Prune files that carry no useful documentation
    try:
        with open(output_file, 'r') as f:
            content = json.load(f)
        keys = set(content[0].keys())
        if keys <= {'directives', 'source'} or len(keys) <= 2:
            os.remove(output_file)
            return False
    except (json.JSONDecodeError, IndexError):
        os.remove(output_file)
        return False

    return True

class DartDocGenerator:
    @staticmethod
    def generate_json(
        source_dir: str,
        output_dir: str,
        version: str = None,
        workers: int = 0,
    ) -> str:
        """
        Generates JSON documentation for all Dart files within the source directory.
        This method walks through all directories under `source_dir` and processes each
        Dart file by generating a JSON documentation file using the 'dartdoc_json' tool.
        If a file with the same name already exists in the output directory, a numeric suffix
        is added to avoid overwriting existing files.
        Args:
            source_dir (str): The directory containing the Dart files to document.
            output_dir (str): The base directory where the generated JSON documentation files will be stored.
            version (str, optional): Version string to create a versioned subdirectory (e.g., "v2.2.0").
                                    If provided, files will be saved to output_dir/{version}/
            workers (int): Number of parallel worker threads.
                0 (default) = auto-detect (min(8, cpu_count)).
        Returns:
            str: The actual output directory path where files were saved.

        Note:
            - Requires the 'dartdoc_json' tool to be installed and accessible in the system path.
            - The source directory must be set through the class initialization or other methods.
        """
        # If version is provided, create a versioned subdirectory
        if version:
            output_dir = os.path.join(output_dir, version)

        # Check if source directory exists
        if not os.path.exists(source_dir) or not os.path.isdir(source_dir):
            raise ValueError(f"Source directory '{source_dir}' does not exist or is not a directory")

        # Check if output directory exists, create if needed (including parent dirs)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        elif not os.path.isdir(output_dir):
            raise ValueError(f"Output directory '{output_dir}' is not a directory")

        # Remove all files in the output directory
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Collect all Dart source files
        dart_files = []
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.dart'):
                    dart_files.append(
                        (file, os.path.join(root, file))
                    )

        # Resolve worker count: 0 = auto (min 8, cpu_count)
        num_workers = workers if workers > 0 else min(
            8, os.cpu_count() or 4
        )

        # Shared lock protects filename allocation only —
        # subprocess execution runs outside the lock.
        lock = threading.Lock()

        with tqdm(
            total=len(dart_files),
            desc="Generating JSON docs",
        ) as pbar:
            with ThreadPoolExecutor(
                max_workers=num_workers,
            ) as executor:
                futures = {
                    executor.submit(
                        _process_file,
                        file, file_path,
                        output_dir, lock,
                    ): file
                    for file, file_path in dart_files
                }
                for future in as_completed(futures):
                    future.result()  # re-raise worker exceptions
                    pbar.update(1)

        return output_dir

if __name__ == "__main__":
    source_dir = os.path.join(os.path.dirname(__file__), "../mekari-pixel/mekari-pixel")
    output_dir = os.path.join(os.path.dirname(__file__), "../dataset")
    
    DartDocGenerator.generate_json(
        source_dir=source_dir,
        output_dir=output_dir
    )