import shutil
from os import popen
from os.path import sep

PROGRAM_NAME = 'MultiBootUsb'

run_cmd = F'python -m PyInstaller -y -F -w --name={PROGRAM_NAME} ' \
          F'..{sep}main.py ' \
          F'--add-data "..{sep}icons;icons" ' \
          F'--add-data "..{sep}data;data" ' \
          F'-i "..{sep}icons{sep}favicon.ico" '


process = popen(run_cmd)
preprocessed = process.read()
process.close()

shutil.rmtree('build')
try:
    shutil.move(F'dist{sep}{PROGRAM_NAME}', '.')
except Exception as e:
    print(F'Could not move files under dist{sep}{PROGRAM_NAME}')
try:
    shutil.move(F'dist{sep}{PROGRAM_NAME}.exe', '.')
except Exception as e:
    print(F'Could not move dist{sep}{PROGRAM_NAME}.exe')
shutil.rmtree('dist')
