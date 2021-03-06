import os
import sys
from enum import Enum
from os.path import sep
import PySimpleGUI as sg

from multibootusb.grub import init_base_grub, add_grub_menu_entry
from multibootusb.iso import extract_basic_efi_directory, list_iso_files
from multibootusb.drive import list_drives, FsTypes
from multibootusb.misc import get_resource_path

if sys.platform == 'linux':
    pass
elif sys.platform == 'win32':
    from multibootusb.drive import win_format_drive as format_drive


class WindowStrings:
    WindowTitleShort = 'MBU'
    WindowTitle = 'Multi-Boot USB'
    RefreshDrives = 'Refresh drives'
    BootEntries = 'Add boot entries'
    FormatDrive = 'Format Drive'


class GuiKeys(Enum):
    FS_TYPE = '-fs_type-'
    ONLY_REMOVABLE = '-only_removable-'
    DRIVES = '-drives-'
    PROGRESS = '-progress-'


class Gui(object):
    def __init__(self):
        self.window = None
        sg.change_look_and_feel('DarkAmber')

        self.icon = get_resource_path(F'icons{sep}favicon.ico')
        self.progress_bar_format = sg.ProgressBar(10, orientation='h', size=(20, 20), key=GuiKeys.PROGRESS)
        self.list_of_drives = sg.Listbox(values=[' '], size=(55, 10), select_mode=sg.SELECT_MODE_SINGLE, no_scrollbar=True,
                                         font=('Courier', 12), key=GuiKeys.DRIVES)
        self.layout = [
            [sg.Text(WindowStrings.WindowTitle, size=(45, 1), font=('Helvetica', 15))],
            [sg.Text('{:5} {:>7} {:>15}  '.format('Drive', 'Total', 'Used'), font=('Courier', 12)),
             sg.Checkbox('Only removable', default=True, key=GuiKeys.ONLY_REMOVABLE),
             sg.Button(WindowStrings.RefreshDrives)],
            [self.list_of_drives],
            [sg.Combo(values=[e.value for e in FsTypes], default_value=FsTypes.FAT32.value, size=(8, 1), key=GuiKeys.FS_TYPE),
             sg.Button(WindowStrings.FormatDrive, button_color=('white', 'red'), bind_return_key=True),
             self.progress_bar_format],
            [],
            [sg.Button(WindowStrings.BootEntries, button_color=('white', 'DarkOrange2')),
             sg.Exit(button_color=('white', 'sea green'))]]

    def start(self):
        self.window = sg.Window(WindowStrings.WindowTitleShort, self.layout,
                                keep_on_top=False,
                                auto_size_buttons=True,
                                default_button_element_size=(12, 1),
                                return_keyboard_events=True,
                                finalize=True,
                                icon=self.icon,
                                )
        self.window[GuiKeys.DRIVES].update(list_drives())

        while True:
            event, values = self.window.read()
            if event in (None, 'Exit'):
                break
            # skip mouse, control key and shift key events entirely
            if 'Mouse' in event or 'Control' in event or 'Shift' in event:
                continue

            if event == WindowStrings.RefreshDrives:
                drives = list_drives(values[GuiKeys.ONLY_REMOVABLE])
                self.window[GuiKeys.DRIVES].update(drives)
            elif event == WindowStrings.BootEntries:
                if sg.popup_yes_no('About to add boot entries.', 'Are you sure ISO files are stored in /isos folder on selected drive?',
                                   keep_on_top=True,
                                   icon=self.icon) == 'Yes':
                    drives = values[GuiKeys.DRIVES]
                    for drive in drives:
                        if drive.fs_type != 'FAT32':
                            if sg.popup_yes_no(F'Non FAT32 drives (as {drive.mount_point}) may not work as multi boot device. Continue?',
                                               keep_on_top=True,
                                               icon=self.icon) == 'No':
                                break
                        isos_path = os.path.join(drive.mount_point, 'isos')
                        efi_path = os.path.join(drive.mount_point, 'EFI')
                        usb_label = drive.get_drive_label()
                        if os.path.exists(isos_path):
                            if not os.path.exists(efi_path):
                                if sg.popup_yes_no(F'There is no /EFI dir on the device {drive.mount_point}, extract default one?',
                                                   keep_on_top=True,
                                                   icon=self.icon) == 'Yes':
                                    extract_basic_efi_directory(get_resource_path(os.path.join('data', 'EFI.zip')), efi_path)
                                else:
                                    sg.popup(F'Adding boot entries aborted!', keep_on_top=True, icon=self.icon)
                                    break
                            grub_path = os.path.join(efi_path, 'BOOT', 'grub.cfg')
                            init_base_grub(grub_path)
                            added_entries = []
                            for iso_file, iso_label in list_iso_files(isos_path):
                                entry_added = add_grub_menu_entry(iso_file, iso_label, grub_path, usb_label)
                                if entry_added is False:
                                    pass  # TODO allow to add entry manually
                                else:
                                    added_entries.append(F"[{iso_label}]{iso_file}")
                            self.window.disable()
                            sg.popup("{} ".format('\n'.join(added_entries)), title='Entries added', icon=self.icon)
                            self.window.enable()
                            self.window.hide()
                            self.window.un_hide()
                        else:
                            sg.popup(F'No "isos" dir on {drive.mount_point}', title='Error', keep_on_top=True, icon=self.icon)
            elif event == WindowStrings.FormatDrive:
                drives = values[GuiKeys.DRIVES]
                for drive in drives:
                    if sg.popup_yes_no(F"You are about to clear out the {drive.device} drive. All your data WILL BE GONE.\nDo you want to continue with {values[GuiKeys.FS_TYPE]}?",
                                       title='Caution',
                                       keep_on_top=True,
                                       icon=self.icon) == 'Yes':
                        success, ret_code = format_drive(drive.device, values[GuiKeys.FS_TYPE],
                                                         only_removable=values[GuiKeys.ONLY_REMOVABLE],
                                                         progress_bar=self.progress_bar_format)
                        if success is True:
                            sg.popup('Drive formatted.', title='Success')
                        else:
                            sg.popup(F'Error 0x{ret_code:08X}.\nThere were some problems while formatting the drive!', title='Error')
                        self.progress_bar_format.update_bar(0, 0)

        self.window.close()
