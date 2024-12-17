import argparse
import os.path
import shutil
import subprocess
import sys

def compress(input_file_path, output_file_path, level = 1):
  """
  Compression levels:
    0: default - almost identical to /screen, 72 dpi images
    1: prepress - high quality, color preserving, 300 dpi imgs
    2: printer - high quality, 300 dpi images
    3: ebook - low quality, 150 dpi images
    4: screen - screen-view-only quality, 72 dpi images
  """
    quality = {0: "/default", 1: "/prepress", 2: "/printer", 3: "/ebook", 4: "/screen"}
    gs = get_ghostscript_path()
    print("Start compressing...")
    initial_size = os.path.getsize(input_file_path) / 1000000
    subprocess.call(
        [
            gs,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS={}".format(quality[level]),
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-sOutputFile={}".format(output_file_path),
            input_file_path,
        ]
    )
    final_size = os.path.getsize(output_file_path) / 1000000
    ratio = 1 - (final_size / initial_size)
    print(f"Compressed by {ratio:.0%}: {initial_size:.2f}MB -> {final_size:.2f}MB")

def get_ghostscript_path():
    gs_names = ["gs", "gswin32", "gswin64"]
    for name in gs_names:
        if shutil.which(name):
            return shutil.which(name)
    raise FileNotFoundError(f"No GhostScript executable was found on path ({'/'.join(gs_names)})")
