#!/bin/bash

if ! type grub2-install > /dev/null; then
    echo "You need grub2 in your system, please yum install grub2"
    exit 1
fi
if rpm -q grub2-efi-modules > /dev/null; then
    echo "You need grub2-efi-modules in your system, please yum install grub2-efi-modules"
    exit 1
fi
if ! type mkfs.fat > /dev/null; then
    echo "You need dosfstools in your system, please yum install dosfstools"
    exit 1
fi


if [[ $# -ne 1 ]]; then
    echo "You have to provide path to usb device."
    echo ""
    echo "Example: ./this_script /dev/sdX"
    exit 1
fi

if [[ ${EUID} -ne 0 ]]; then
    echo "This script requires sudo to run."
    exit 1
fi

DST_DEVICE=$1

if ! [[ ${DST_DEVICE} =~ ^/dev/sd[a-z]+$ ]];then
    echo "It looks like you have entered invalid device path (do not use specific partition, provide block device)."
    exit 1
fi

echo "Whole device will be reformatted, all data stored on ${DST_DEVICE} will be lost."
read -p "Are you sure you want to continue? [y/N]: " -r
if ! [[ ${REPLY} =~ ^[Yy]$ ]]; then
    echo "Operation canceled, no changes were done."
    exit 1
fi

umount "${DST_DEVICE}?*"
parted -s ${DST_DEVICE} mklabel msdos  # create MBR
parted -s ${DST_DEVICE} mkpart primary 1MiB 551MiB  # create EFI partition sdX1

parted -s ${DST_DEVICE} set 1 esp on
parted -s ${DST_DEVICE} set 1 boot on

mkfs.fat -F 32 "${DST_DEVICE}1"  # create fat32 fs on efi partition sdX1
parted -s ${DST_DEVICE} mkpart primary 551MiB 100%  # create second partition after EFI and use rest of the device
mkfs.fat -F 32 "${DST_DEVICE}2"  # it could be ext4 but it wont show on windows

# mount created partitions
TMP_MOUNT=$(mktemp -d)
TMP_MOUNT_EFI="${TMP_MOUNT}/efi"
TMP_MOUNT_DATA="${TMP_MOUNT}/data"
mkdir ${TMP_MOUNT_EFI}
mkdir ${TMP_MOUNT_DATA}
mount "${DST_DEVICE}1" ${TMP_MOUNT_EFI}
mount "${DST_DEVICE}2" ${TMP_MOUNT_DATA}


grub2-install --target=i386-pc --recheck --boot-directory="${TMP_MOUNT_DATA}/[BOOT]" "${DST_DEVICE}"
grub2-install --target=x86_64-efi --recheck --removable --efi-directory="${TMP_MOUNT_EFI}" --boot-directory="${TMP_MOUNT_DATA}/[BOOT]"
touch "${TMP_MOUNT_DATA}/[BOOT]/grub2/grub.cfg"

# umount partitions && remove mount points
umount ${TMP_MOUNT_EFI} && rmdir ${TMP_MOUNT_EFI}
umount ${TMP_MOUNT_DATA} && rmdir ${TMP_MOUNT_DATA}
rmdir ${TMP_MOUNT}

















