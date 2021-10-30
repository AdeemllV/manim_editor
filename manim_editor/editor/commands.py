import subprocess
import os
import json
import jsonschema
from typing import List, Optional, Tuple, Generator, Any

from .config import get_config


def capture(command: List[str],
            cwd: Optional[str] = None,
            command_input: Optional[str] = None) -> Tuple[str, str, int]:
    """Run command and capture standard output, standard error and return code."""
    p = subprocess.run(command, cwd=cwd, input=command_input, capture_output=True, text=True)
    out, err = p.stdout, p.stderr
    return out, err, p.returncode


def capture_ffmpeg(params: List[str]) -> Tuple[str, str, int]:
    """Run ffmpeg with params and capture standard output, standard error and return code."""
    return capture(["ffmpeg"] + params)


def run_ffmpeg(params: List[str]) -> bool:
    """Run ffmpeg with params and loglevel defined in config, print output to terminal and return True at success."""
    return subprocess.call(["ffmpeg", "-loglevel", get_config().FFMPEG_LOGLEVEL] + params) == 0


def walk(top: str, maxdepth: int) -> Generator[Tuple[str, List[str], List[str]], None, None]:
    """Reimplementation of os.walk with max recursion depth."""
    dirs: List[str] = []
    nondirs: List[str] = []
    for name in os.listdir(top):
        if os.path.isdir(os.path.join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)
    yield top, dirs, nondirs
    if maxdepth:
        for name in dirs:
            for res in walk(os.path.join(top, name), maxdepth-1):
                yield res


def valid_json_load(path: str, schema: Any) -> Optional[Any]:
    """Load json file from path and validate with schema.
    Return ``None`` when json is invalid.
    """
    if not os.path.isfile(path):
        return None
    with open(path, "r") as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            return None
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError:
        return None
    return data