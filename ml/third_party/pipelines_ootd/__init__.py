"""
Compatibility package for OOTDiffusion custom module imports.

Some checkpoints/configs reference modules as `pipelines_ootd.*` while the
actual sources live in `ootd/pipelines_ootd`. Expose that directory as this
package path so both import styles work.
"""

from pathlib import Path

_CURRENT_DIR = Path(__file__).resolve().parent
_OOTD_PIPELINES_DIR = _CURRENT_DIR.parent / "ootd" / "pipelines_ootd"

# Make `import pipelines_ootd.<module>` load files from `ml/third_party/ootd/pipelines_ootd`.
__path__ = [str(_OOTD_PIPELINES_DIR)]
