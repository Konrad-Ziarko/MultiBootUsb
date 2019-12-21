import os
from os.path import sep
import PySimpleGUI as sg

from multibootusb.grub import init_base_grub, add_rhel_menu_entry
from multibootusb.iso import extract_basic_efi_directory, list_iso_files
from multibootusb.drive import list_drives
from multibootusb.misc import get_resource_path


class WindowStrings:
    WindowTitleShort = 'MBU'
    WindowTitle = 'Multi-Boot USB'
    RefreshDrives = 'Refresh drives'
    BootEntries = 'Add boot entries'
    FormatDrive = 'Format Drive'


class Gui(object):
    def __init__(self):
        self.window = None
        sg.change_look_and_feel('DarkAmber')

        self.icon = get_resource_path(F'icons{sep}favicon.ico')
        self.layout = [[sg.Text(WindowStrings.WindowTitle, size=(45, 1), font=('Helvetica', 15))],
                       [sg.Text('{:5} {:>9} {:>9}'.format('Drive', 'Total', 'Used'), font=('Courier', 12)),
                        sg.Checkbox('Only removable', default=True, key='-only_removable-'),
                        sg.Button(WindowStrings.RefreshDrives)],
                       [sg.Listbox(values=[' '], size=(50, 10), select_mode=sg.SELECT_MODE_SINGLE, font=('Courier', 12), key='-drives-')],
                       [sg.Button(WindowStrings.BootEntries, button_color=('white', 'DarkOrange2')),
                        sg.Button(WindowStrings.FormatDrive, button_color=('white', 'red'), bind_return_key=True),
                        sg.Exit(button_color=('white', 'sea green'))]]

    def start(self):
        self.window = sg.Window(WindowStrings.WindowTitleShort, self.layout,
                                keep_on_top=False,
                                auto_size_buttons=False,
                                default_button_element_size=(12, 1),
                                return_keyboard_events=True,
                                finalize=True,
                                icon=self.icon)
        drives = list_drives()
        self.window['-drives-'].update(drives)

        while True:
            event, values = self.window.read()
            if event in (None, 'Exit'):
                break
            # skip mouse, control key and shift key events entirely
            if 'Mouse' in event or 'Control' in event or 'Shift' in event:
                continue

            if event == WindowStrings.RefreshDrives:
                drives = list_drives(values['-only_removable-'])
                self.window['-drives-'].update(drives)
            elif event == WindowStrings.BootEntries:
                if sg.popup_yes_no('About to add boot entries.', 'Are you sure ISO files are stored in /isos folder on selected drive?', keep_on_top=True, icon=self.icon) == 'Yes':
                    drives = values['-drives-']
                    for drive in drives:
                        if drive.fs_type != 'FAT32':
                            if sg.popup_yes_no(F'Non FAT32 drives (as {drive.mount_point}) may not work as multi boot device. Continue?', keep_on_top=True, icon=self.icon) == 'No':
                                break
                        isos_path = os.path.join(drive.mount_point, 'isos')
                        efi_path = os.path.join(drive.mount_point, 'EFI')
                        if os.path.exists(isos_path):
                            if not os.path.exists(efi_path):
                                if sg.popup_yes_no(F'There is no /EFI dir on the device {drive.mount_point}, extract default one?', keep_on_top=True, icon=self.icon) == 'Yes':
                                    extract_basic_efi_directory(get_resource_path(os.path.join('data', 'EFI.zip')), efi_path)
                                else:
                                    sg.popup(F'Adding boot entries aborted!', keep_on_top=True, icon=self.icon)
                                    break
                            else:
                                grub_path = os.path.join(efi_path, 'BOOT', 'grub.cfg')
                                init_base_grub(grub_path)
                                for iso_file, iso_label in list_iso_files(isos_path):
                                    if 'centos' in iso_file.lower():
                                        add_rhel_menu_entry(grub_path, iso_label, iso_file)
                        else:
                            sg.popup(F'No "isos" dir on {drive.mount_point}', title='Error', keep_on_top=True, icon=self.icon)
            elif event == WindowStrings.FormatDrive:
                pass

        self.window.close()