"""Compatibility entry point for the current character manifest validator."""
from pathlib import Path
import runpy


def main():
    runpy.run_path(str(Path(__file__).resolve().parents[1] / 'qdao_character_diversity_v9/build_manifest.py'), run_name='__main__')


if __name__ == '__main__':
    main()
