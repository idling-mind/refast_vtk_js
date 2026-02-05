"""Custom Hatch build hook to build frontend assets before packaging."""

import os
import subprocess
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Build hook that compiles the React frontend before packaging."""

    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """
        Build the frontend assets before the package is built.

        This hook runs `npm install` and `npm run build` in the frontend
        directory to compile the React components into a UMD bundle.
        """
        root = Path(self.root)
        frontend_dir = root / "frontend"
        static_dir = root / "src" / "refast_vtk_js" / "static"

        # Skip if we're in an sdist (source already built) or static exists
        if not frontend_dir.exists():
            self.app.display_info("Frontend directory not found, skipping build")
            return

        # Check if npm is available
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        
        try:
            subprocess.run(
                [npm_cmd, "--version"],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            if static_dir.exists() and any(static_dir.iterdir()):
                self.app.display_info(
                    "npm not found but static files exist, skipping build"
                )
                return
            raise RuntimeError(
                "npm is required to build the frontend. "
                "Please install Node.js or pre-build the frontend."
            )

        self.app.display_info("Installing frontend dependencies...")
        subprocess.run(
            [npm_cmd, "install"],
            cwd=frontend_dir,
            check=True,
            shell=(os.name == "nt"),
        )

        self.app.display_info("Building frontend assets...")
        subprocess.run(
            [npm_cmd, "run", "build"],
            cwd=frontend_dir,
            check=True,
            shell=(os.name == "nt"),
        )

        # Verify build output exists
        if not static_dir.exists() or not any(static_dir.iterdir()):
            raise RuntimeError(
                f"Frontend build did not produce output in {static_dir}"
            )

        self.app.display_info("Frontend build complete!")
