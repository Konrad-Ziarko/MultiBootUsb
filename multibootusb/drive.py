import io
from psutil import disk_partitions, disk_usage
from typing import List


GB = 2 ** 30


class MBUDrive(object):

    def __init__(self, psutil_drive):
        self.drive = psutil_drive.device
        self.fs_type = psutil_drive.fstype
        self.opts = psutil_drive.opts
        self.mount_point = psutil_drive.mountpoint

        self.size_total = disk_usage(self.drive).total
        self.size_used = disk_usage(self.drive).used
        self.size_free = disk_usage(self.drive).free
        self.size_percent = disk_usage(self.drive).percent

    def __str__(self):
        return F'{self.drive:5} {self.size_total / GB:9.3f} {self.size_used / GB:9.3f}'


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


class WinFsTypes:
    EXFAT = 'exFAT'
    FAT = 'FAT'
    FAT32 = 'FAT32'
    NTFS = 'NTFS'


def win_format_drive(windows_drive_letter: str, fs_type: str = WinFsTypes.FAT32, drive_label: str = ''):
    from ctypes import windll, c_int, c_void_p, c_wchar_p, WINFUNCTYPE
    fm = windll.LoadLibrary('fmifs.dll')
    fmt_cb_func = WINFUNCTYPE(c_int, c_int, c_int, c_void_p)

    fmifs_harddisk = 0x0C

    def my_fmt_callback(command, modifier, arg):
        print(command, modifier, arg)
        return 1  # TRUE

    windows_drive_letter = windows_drive_letter.upper()
    if not windows_drive_letter.endswith(':\\'):
        windows_drive_letter += ':\\'

    fm.FormatEx(c_wchar_p(windows_drive_letter), fmifs_harddisk, c_wchar_p(fs_type),
                c_wchar_p(drive_label), True, c_int(0), fmt_cb_func(my_fmt_callback))
