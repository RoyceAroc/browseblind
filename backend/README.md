## Development Guide
Below are instructions for development purposes.
### Local Set Up
conda create --name browseblind-package python=3.9.7
conda activate browseblind-package
conda install -c conda-forge poetry
poetry install
poetry shell
sudo python backend/src/main.py

### Installing packages
poetry install <package name>

