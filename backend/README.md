## Development Guide
Below are instructions for development purposes.
### Local Set Up
conda create --name browseblind
conda activate browseblind
poetry install

### Installing packages
poetry install <package name>

## Packing application
poetry shell
pyinstaller --clean --windowed src/main.py

