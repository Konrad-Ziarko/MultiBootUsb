import io
import sys
from enum import Enum
from typing import List

from psutil import disk_partitions, disk_usage

from multibootusb.misc import ProgressBarProgress, DummyProgressBar, bytes2human

GB = 2 ** 30

if sys.platform == 'linux':
    pass
elif sys.platform == 'win32':
    def _drive_label(device_path):
        from ctypes import windll, create_unicode_buffer, c_wchar_p, sizeof
        kernel32 = windll.kernel32
        volume_name_buffer = create_unicode_buffer(1024)
        file_system_name_buffer = create_unicode_buffer(1024)
        serial_number = None
        max_component_length = None
        file_system_flags = None

        rc = kernel32.GetVolumeInformationW(
            c_wchar_p(device_path),
            volume_name_buffer,
            sizeof(volume_name_buffer),
            serial_number,
            max_component_length,
            file_system_flags,
            file_system_name_buffer,
            sizeof(file_system_name_buffer)
        )
        return volume_name_buffer.value


class MBUDrive(object):

    def __init__(self, psutil_drive):
        self.device = psutil_drive.device
        self.fs_type = psutil_drive.fstype
        self.opts = psutil_drive.opts
        self.mount_point = psutil_drive.mountpoint

        self.size_total = disk_usage(self.mount_point).total
        self.size_used = disk_usage(self.mount_point).used
        self.size_free = disk_usage(self.mount_point).free
        self.size_percent = disk_usage(self.mount_point).percent

    def __str__(self):
        device = self.device
        if device.startswith('/dev/'):
            device = device.replace('/dev/', '')
        return F'{device:5} {bytes2human(self.size_total):>7} {bytes2human(self.size_used):>9}({self.size_percent:4}%)  {self.fs_type:6} [{self.mount_point}]'

    def get_drive_label(self):
        return _drive_label(self.device)


def list_drives(only_removable: bool = True) -> List[MBUDrive]:
    psutil_drives = disk_partitions()
    drives = [MBUDrive(drive) for drive in psutil_drives if 'removable' in drive.opts or not only_removable]
    return drives


def clear_drive(device_path: str, block_size: int = 4096) -> None:
    block = b'\0' * block_size
    try:
        with io.FileIO(device_path, 'w') as device:
            while device.write(block):
                pass
    except IOError as err:
        raise IOError(F'Could not clear device {device_path} due to an error: {err}')


class FsTypes(Enum):
    EXFAT = 'exFAT'
    FAT = 'FAT'
    FAT32 = 'FAT32'
    NTFS = 'NTFS'


class FMIFS:
    UNKNOWN = 0x00
    REMOVABLE = 0x0B
    HARD_DISK = 0x0C


def win_format_drive(windows_drive_letter: str, fs_type: str = FsTypes.FAT32.value, drive_label: str = '', only_removable=True, progress_bar=DummyProgressBar()):
    from ctypes import windll, c_int, c_void_p, c_wchar_p, WINFUNCTYPE
    fm = windll.LoadLibrary('fmifs.dll')
    fmt_cb_func = WINFUNCTYPE(c_int, c_int, c_int, c_void_p)
    progress = ProgressBarProgress()

    def my_fmt_callback(command, modifier, arg):
        progress_bar.update_bar(progress.value(), 5)
        progress.increment()
        return 1  # TRUE

    windows_drive_letter = windows_drive_letter.upper()
    if not windows_drive_letter.endswith(':\\'):
        windows_drive_letter += ':\\'

    device_type = FMIFS.UNKNOWN
    if only_removable is True:
        device_type = FMIFS.REMOVABLE

    ret_code = fm.FormatEx(c_wchar_p(windows_drive_letter), device_type, c_wchar_p(fs_type),
                           c_wchar_p(drive_label), True, c_int(0), fmt_cb_func(my_fmt_callback))
    progress_bar.update_bar(5, 5)
    return ret_code == 0x6774128C, ret_code
