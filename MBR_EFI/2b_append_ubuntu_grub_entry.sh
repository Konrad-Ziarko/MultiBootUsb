#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "You have to provide path to iso and path to grub on your usb stick."
    echo ""
    echo "Example: ./this_script /mnt/boot/iso/centos.iso /mnt/boot/grub2/grub.cfg"
    exit
fi

if [[ ${EUID} -ne 0 ]]; then
    echo "Pleas run this script as sudo."
    exit
fi
ISO_FILE=$1
ISO_NAME="${ISO_FILE##*/}"
GRUB_FILE=$2
LABEL=$(dd if="${ISO_FILE}" bs=1 skip=32808 count=32 status=none | sed 's/ *$//g')

ISO_VAR='${isofile}'

cat >> "${GRUB_FILE}" << EOT
menuentry "${LABEL}" {
    isofile="/boot/iso/${ISO_NAME}"
    loopback loop "${ISO_VAR}"
    linux (loop)/casper/vmlinuz iso-scan/filename="${ISO_VAR}" boot=casper quiet splash
    initrd (loop)/casper/initrd
}

EOT





