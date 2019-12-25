

def init_base_grub(grub_path):
    with open(grub_path, 'w+') as grub_file:
        grub_file.write("""
set default="1"

function load_video {
  insmod efi_gop
  insmod efi_uga
  insmod video_bochs
  insmod video_cirrus
  insmod all_video
}

load_video
set gfxpayload=keep
insmod gzio
insmod part_gpt
insmod ext2
insmod loopback
insmod iso9660
insmod udf

set timeout=60

""")


def add_grub_menu_entry(iso_file: str, iso_label: str, grub_path: str, usb_label: str):
    if 'centos' in iso_file.lower() or 'centos' in iso_label.lower():
        _add_rhel_menu_entry(grub_path, iso_label, iso_file, usb_label)
    elif 'archlinux' in iso_file.lower() or 'arch_' in iso_label.lower():
        _add_archlinux_menu_entry(grub_path, iso_label, iso_file, usb_label)
    elif 'ubuntu' in iso_file.lower() or 'ubuntu' in iso_label.lower():
        _add_ubuntu_menu_entry(grub_path, iso_label, iso_file, usb_label)
    elif (('debian' in iso_file.lower() or 'debian' in iso_label.lower())
          and ('live' in iso_file.lower() or 'live' in iso_label.lower())):
        _add_debian_menu_entry(grub_path, iso_label, iso_file, usb_label)
    elif 'systemrescue' in iso_file.lower() or 'system rescue' in iso_label.lower():
        _add_system_rescue_menu_entry(grub_path, iso_label, iso_file, usb_label)
    else:
        return False
    return True


def _add_system_rescue_menu_entry(grub_path: str, iso_label: str, entry_iso_path: str, usb_label: str):
    escaped_iso_label = iso_label.replace(' ', r'\x20')
    escaped_entry_iso_path = entry_iso_path.replace(' ', r'\x20')
    with open(grub_path, 'a') as grub_file:
        grub_file.write(f'menuentry \'{iso_label}\' {{\n'
                        f'\tset isofile="/isos/{escaped_entry_iso_path}"\n'
                        '\texport isofile\n'
                        '\tsearch --file $isofile\n'
                        '\tloopback loop $isofile\n'
                        '\techo "Loading kernel..."\n'
                        f'\tlinuxefi (loop)/sysresccd/boot/x86_64/vmlinuz scandelay=1 dostartx archisobasedir=sysresccd img_label={usb_label} img_loop=/$isofile copytoram\n'
                        '\techo "Loading initrd..."\n'
                        '\tinitrdefi (loop)/sysresccd/boot/intel_ucode.img (loop)/sysresccd/boot/amd_ucode.img (loop)/sysresccd/boot/x86_64/sysresccd.img\n'
                        '}\n'
                        )


def _add_rhel_menu_entry(grub_path: str, iso_label: str, entry_iso_path: str, usb_label: str):
    escaped_iso_label = iso_label.replace(' ', r'\x20')
    escaped_entry_iso_path = entry_iso_path.replace(' ', r'\x20')
    with open(grub_path, 'a') as grub_file:
        grub_file.write(f'menuentry \'{iso_label}\'  --class fedora --class gnu-linux --class gnu --class os {{\n'
                        f'\tset isofile="/isos/{escaped_entry_iso_path}"\n'
                        '\texport isofile\n'
                        '\tsearch --set=root --file $isofile\n'
                        '\tloopback loop $isofile\n'
                        '\techo "Loading kernel..."\n'
                        f'\tlinuxefi (loop)/isolinux/vmlinuz iso-scan/filename=$isofile inst.stage2=hd:LABEL={escaped_iso_label} quiet\n'
                        '\techo "Loading initrd..."\n'
                        '\tinitrdefi (loop)/isolinux/initrd.img\n'
                        '}\n'
                        )


def _add_ubuntu_menu_entry(grub_path: str, iso_label: str, entry_iso_path: str, usb_label: str):
    escaped_iso_label = iso_label.replace(' ', r'\x20')
    escaped_entry_iso_path = entry_iso_path.replace(' ', r'\x20')
    with open(grub_path, 'a') as grub_file:
        grub_file.write(f'menuentry \'{iso_label}\' {{\n'
                        f'\tset isofile="/isos/{escaped_entry_iso_path}"\n'
                        '\texport isofile\n'
                        '\tsearch --set=root --file $isofile\n'
                        '\tloopback loop ${isofile}\n'
                        '\troot=(loop)\n'
                        '\techo "Loading kernel..."\n'
                        '\tlinuxefi /casper/vmlinuz  file=/cdrom/preseed/ubuntu.seed boot=casper iso-scan/filename=$isofile quiet splash ---\n'
                        '\techo "Loading initrd..."\n'
                        '\tinitrdefi /casper/initrd\n'
                        '}\n'
                        )


def _add_debian_menu_entry(grub_path: str, iso_label: str, entry_iso_path: str, usb_label: str):
    escaped_iso_label = iso_label.replace(' ', r'\x20')
    escaped_entry_iso_path = entry_iso_path.replace(' ', r'\x20')
    with open(grub_path, 'a') as grub_file:
        grub_file.write(f'menuentry \'{iso_label}\' {{\n'
                        f'\tset isofile="/isos/{escaped_entry_iso_path}"\n'
                        '\texport isofile\n'
                        '\tsearch --set -f $isofile\n'
                        '\tloopback loop ${isofile}\n'
                        '\techo "Loading kernel..."\n'
                        f'\tlinuxefi (loop)/d-i/vmlinuz boot=live components findiso=$isofile\n'
                        '\techo "Loading initrd..."\n'
                        '\tinitrdefi (loop)/d-i/initrd.gz\n'
                        '}\n'
                        )


def _add_archlinux_menu_entry(grub_path: str, iso_label: str, entry_iso_path: str, usb_label: str):
    escaped_iso_label = iso_label.replace(' ', r'\x20')
    escaped_entry_iso_path = entry_iso_path.replace(' ', r'\x20')
    with open(grub_path, 'a') as grub_file:  # FIXME
        grub_file.write(f'menuentry \'{iso_label}\' {{\n'
                        f'\tset isofile="/isos/{escaped_entry_iso_path}"\n'
                        '\texport isofile\n'
                        '\tsearch --set=root --file $isofile\n'
                        '\tloopback loop $isofile\n'
                        '\techo "Loading kernel..."\n'
                        f'\tlinuxefi (loop)/arch/boot/x86_64/vmlinuz scandelay=1 dostartx archisobasedir=arch img_label={usb_label} img_loop=$isofile\n'
                        '\techo "Loading initrd..."\n'
                        '\tinitrdefi (loop)/arch/boot/intel_ucode.img (loop)/arch/boot/amd_ucode.img (loop)/arch/boot/x86_64/archiso.img\n'
                        '}\n'
                        )
