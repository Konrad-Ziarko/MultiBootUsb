# MultiBootUsb

Few scripts, allowing to make multiboot usb stick, and easly append new ISOs to bootloader.

# Disclaimer
Scripts where written under RHEL7, minor changes may be needed to run this script under Debian or other distros.

# Usage
## 1.Make USB device a multiboot device
Plug USB device and run initialization script on appropriate SCSI device  
`sudo ./init_multiboot_usb.sh /dev/sdX` where `X` stands for your device letter.

## 2.Copy ISO file to your formated device
> Initialization unmounts your drive so start with mounting second partition `mount /dev/sdX2 /mnt`  

copy iso with `cp example.iso /mnt/boot/iso/`

## 3.Append new entry to grub on you multiboot USB
`sudo ./append_rhel_grub_entry.sh /mnt/boot/iso/example.iso /mnt/boot/grub2/grub.cfg`
> Append does not unmount USB drive

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
