"""Orcfax Publication Monitoring.

A lightweight script to help ensure that CER prices are available
within hour-long windows.
"""

from src.pubwatch import pubwatch


def main():
    """Primary entry point for this script."""
    pubwatch.main()


if __name__ == "__main__":
    main()
