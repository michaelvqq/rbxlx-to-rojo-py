#!/usr/bin/env python3
"""Build a standalone desktop release that does not require Python."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "rbxlx-to-rojo"
ROOT = Path(__file__).resolve().parent.parent
ENTRYPOINT = ROOT / "cli.py"
BUILD_VENV = ROOT / ".build-venv"
BUILD_DIR = ROOT / "build"
DIST_DIR = ROOT / "dist"
PYINSTALLER_CONFIG_DIR = ROOT / ".pyinstaller"


def run(cmd: list[str]) -> None:
    """Run a subprocess and fail fast on errors."""
    print("+", " ".join(cmd))
    env = os.environ.copy()
    env["PYINSTALLER_CONFIG_DIR"] = str(PYINSTALLER_CONFIG_DIR)
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def venv_python() -> Path:
    """Return the Python executable inside the build venv."""
    if sys.platform == "win32":
        return BUILD_VENV / "Scripts" / "python.exe"

    return BUILD_VENV / "bin" / "python"


def pyinstaller_data_arg(source: Path, destination: str) -> str:
    """Build an --add-data value for the current platform."""
    return f"{source}{os.pathsep}{destination}"


def local_rbxmk_path() -> Path | None:
    """Return a local rbxmk binary, downloading if necessary."""
    rbxmk = shutil.which("rbxmk")
    if rbxmk:
        return Path(rbxmk)

    # Download rbxmk v0.9.1 if not found in PATH.
    import tempfile
    import zipfile

    platform_mapping = {
        "darwin": "darwin-amd64",
        "win32": "windows-amd64",
        "linux": "linux-amd64",
    }
    platform_suffix = platform_mapping.get(sys.platform)

    if not platform_suffix:
        print(f"Warning: rbxmk download not available for {sys.platform}")
        return None

    print("Downloading rbxmk v0.9.1...")

    # Cache rbxmk in the .pyinstaller directory so it persists across builds.
    cache_dir = PYINSTALLER_CONFIG_DIR / "rbxmk-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached_binary = cache_dir / "rbxmk"

    if cached_binary.exists():
        return cached_binary

    url = f"https://github.com/Anaminus/rbxmk/releases/download/v0.9.1/rbxmk-v0.9.1-{platform_suffix}.zip"

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "rbxmk.zip"

            # Use curl to download (better SSL handling on macOS).
            curl_result = subprocess.run(
                ["curl", "-sS", "-L", url, "-o", str(zip_path)],
                check=False,
            )
            if curl_result.returncode != 0:
                print("Warning: curl failed to download rbxmk")
                return None

            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(tmpdir)

            # Find and extract the rbxmk binary.
            extracted = Path(tmpdir)
            for candidate in extracted.rglob("rbxmk*"):
                if candidate.is_file():
                    # Copy to cache location.
                    shutil.copy2(candidate, cached_binary)
                    cached_binary.chmod(0o755)
                    return cached_binary

        print("Warning: rbxmk not found in downloaded archive")
        return None
    except Exception as e:
        print(f"Warning: Failed to download rbxmk: {e}")
        return None


def ensure_build_environment() -> Path:
    """Create the build venv and install PyInstaller."""
    if not BUILD_VENV.exists():
        run([sys.executable, "-m", "venv", str(BUILD_VENV)])

    python = venv_python()

    try:
        subprocess.run(
            [str(python), "-m", "PyInstaller", "--version"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        try:
            run([str(python), "-m", "pip", "install", "pyinstaller"])
        except subprocess.CalledProcessError as exc:
            raise SystemExit(
                "Could not install PyInstaller. Run the builder on a machine with internet access "
                "or preinstall PyInstaller into .build-venv first."
            ) from exc

    return python


def clean_previous_builds() -> None:
    """Remove old build artifacts."""
    for path in (BUILD_DIR, DIST_DIR):
        if path.exists():
            shutil.rmtree(path)


def build_release(python: Path) -> None:
    """Run PyInstaller."""
    cmd = [
        str(python),
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onedir",
        "--name",
        APP_NAME,
        "--hidden-import",
        "tkinter",
        "--hidden-import",
        "tkinter.filedialog",
        "--hidden-import",
        "tkinter.messagebox",
        str(ENTRYPOINT),
    ]

    bridge_script = ROOT / "scripts" / "parse_binary_place.lua"
    if bridge_script.exists():
        cmd.extend(["--add-data", pyinstaller_data_arg(bridge_script, "scripts")])

    bundled_rbxmk = local_rbxmk_path()
    if bundled_rbxmk is not None:
        cmd.extend(["--add-data", pyinstaller_data_arg(bundled_rbxmk, "bin")])

    run(cmd)


def bundle_path() -> Path:
    """Return the primary built artifact path."""
    if sys.platform == "darwin":
        return DIST_DIR / f"{APP_NAME}.app"

    if sys.platform == "win32":
        return DIST_DIR / APP_NAME / f"{APP_NAME}.exe"

    return DIST_DIR / APP_NAME / APP_NAME


def zip_release() -> Path:
    """Create a zip archive for easy sharing."""
    if sys.platform == "darwin":
        base_name = DIST_DIR / APP_NAME
        shutil.make_archive(str(base_name), "zip", root_dir=DIST_DIR, base_dir=f"{APP_NAME}.app")
        return base_name.with_suffix(".zip")

    base_name = DIST_DIR / APP_NAME
    shutil.make_archive(str(base_name), "zip", root_dir=DIST_DIR, base_dir=APP_NAME)
    return base_name.with_suffix(".zip")


def main() -> None:
    """Build the standalone bootstrapper."""
    if not ENTRYPOINT.exists():
        raise FileNotFoundError(f"Missing entrypoint: {ENTRYPOINT}")

    clean_previous_builds()
    python = ensure_build_environment()
    build_release(python)

    artifact = bundle_path()
    archive = zip_release()

    print()
    print("Standalone release created.")
    print(f"Primary artifact: {artifact}")
    print(f"Shareable archive: {archive}")
    print("Users can run the app directly without installing Python or this repository.")


if __name__ == "__main__":
    main()
