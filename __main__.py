import os

import scraper

image = scraper.scrap_for_image()
# Only changes when run from terminal
os.system(f"gsettings set org.gnome.desktop.background picture-uri-dark file://{image}")