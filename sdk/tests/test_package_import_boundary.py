import os
import subprocess
import sys
import textwrap
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parents[1]


def test_engine_submodule_import_does_not_require_http_client():
    code = textwrap.dedent(
        """
        import builtins
        import sys

        real_import = builtins.__import__

        def block_httpx(name, *args, **kwargs):
            if name == "httpx":
                raise ModuleNotFoundError("httpx intentionally unavailable")
            return real_import(name, *args, **kwargs)

        builtins.__import__ = block_httpx

        import noosphere.engine.memory_integrity

        assert "noosphere.client" not in sys.modules
        """
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SDK_ROOT)

    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=SDK_ROOT.parent,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr


def test_public_noosphere_client_export_remains_available():
    from noosphere import Noosphere
    from noosphere.client import Noosphere as Client

    assert Noosphere is Client
