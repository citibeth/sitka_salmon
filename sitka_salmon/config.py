import os

# Locate data files
try:
    # Running on Google Colab?  Use files from Google Drive
    import google.colab
    google.colab.drive.mount("/content/drive")
    HARNESS = '/content/drive/MyDrive/sitka_salmon'
except ModuleNotFoundError:
    # Running locally, key off of location of source in the filesystem
    HARNESS = os.path.abspath(os.path.os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
