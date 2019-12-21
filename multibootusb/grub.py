

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

set timeout=60

""")


def add_rhel_menu_entry(grub_path, iso_label, entry_iso_path):
    escaped_label = iso_label.replace(' ', r'\x20')
    with open(grub_path, 'a') as grub_file:
        grub_file.write(f'menuentry \'{iso_label}\'  --class fedora --class gnu-linux --class gnu --class os {{\n'
                        f'\tisofile="/isos/{entry_iso_path}"\n'
                        '\tloopback loop ${isofile}\n'
                        f'\tlinuxefi (loop)/isolinux/vmlinuz iso-scan/filename=${{isofile}} inst.stage2=hd:LABEL={escaped_label} quiet\n'
                        '\tinitrdefi (loop)/isolinux/initrd.img\n'
                        '}\n'
                        )


def add_ubuntu_menu_entry(grub_path, iso_label, entry_iso_path):
    with open(grub_path, 'a') as grub_file:
        grub_file.write(f'menuentry \'{iso_label}\' {{'
                        f'isofile="/isos/{entry_iso_path}"'
                        'loopback loop ${isofile}'
                        f'linuxefi (loop)/isolinux/vmlinuz iso-scan/filename=${{isofile}} boot=casper quiet splash'
                        'initrdefi (loop)/isolinux/initrd.img'
                        '}'
                        )
