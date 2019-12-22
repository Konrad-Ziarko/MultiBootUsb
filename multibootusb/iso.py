import os
import shutil

import pycdlib


def list_iso_files(base_path):
    for dirpath, _, filenames in os.walk(base_path):
        for filename in (f for f in filenames if f.endswith(".iso")):
            new_dir = dirpath.replace(base_path, '')
            path = os.path.join(new_dir, filename).replace('\\', '/')
            if path.startswith('/'):
                path = path[1:]
            label = get_iso_label(os.path.join(dirpath, filename))
            yield path, label


def extract_basic_efi_directory(path_to_zip, unpack_path):
    shutil.unpack_archive(path_to_zip, unpack_path, 'zip')


def get_iso_label(iso_path: str, strip: bool = True) -> str:
    try:
        with open(iso_path, 'rb') as iso_file:
            iso_file.seek(32808)
            label = iso_file.read(32).decode('utf-8')
            if strip is True:
                label = label.strip()
            return label
    except IOError as err:
        raise IOError(F'Could not retrieve iso label from {iso_file} due to an error: {err}')


def _get_directort_from_iso(iso, relative_path, extract_destination):
    for child in iso.list_children(iso_path=relative_path):
        if child.file_identifier() == b'.' or child.file_identifier() == b'..':
            pass
        elif child.file_identifier().decode('utf-8').endswith(';1'):
            iso.get_file_from_iso(iso_path=relative_path+'/'+child.file_identifier().decode("utf-8"),
                                  local_path=os.path.join(extract_destination, child.file_identifier().decode('utf-8'))[:-2])
        else:
            tmp_path = os.path.join(extract_destination, child.file_identifier().decode('utf-8'))
            os.mkdir(tmp_path)
            _get_directort_from_iso(iso, relative_path+'/'+child.file_identifier().decode('utf-8'), tmp_path)


def get_directory_from_iso(path_to_iso, extract_destination='', directory_name='EFI'):
    if extract_destination == '':
        return None

    iso = pycdlib.PyCdlib()
    iso.open(path_to_iso)
    relative_path = '/'
    for child in iso.list_children(iso_path='/'):
        if child.file_identifier() == directory_name.encode('utf-8'):
            os.mkdir(os.path.join(extract_destination, directory_name), )
            _get_directort_from_iso(iso, relative_path+directory_name, os.path.join(extract_destination, directory_name))
    iso.close()

