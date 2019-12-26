# MultiBootUsb
![](https://img.shields.io/github/issues/Konrad-Ziarko/MultiBootUsb.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/258e003beaa444a3babd651f89086f26)](https://www.codacy.com/manual/Konrad-Ziarko/MultiBootUsb?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Konrad-Ziarko/MultiBootUsb&amp;utm_campaign=Badge_Grade)
![](https://img.shields.io/github/license/Konrad-Ziarko/MultiBootUsb.svg)

GUI application for quickly adding boot entries on MultiBoot USB devices

# Disclaimer
Grub entries were written for:
- RHEL 
- CentOs  
- Ubuntu  
- Debian live  
- SystemRescueCD  
- ~~ArchLinux~~ # Ends up in tty mode

## Build from source
*Run [script](installer/installer.py) stored in installer folder*

# Usage
1. Place .iso files in /isos directory on the drive
2. Select desired removable drive from the list
3. Click 'Add boot entries' button
4. Follow popup windows to finish the process

![Main window](docs/images/screen1.png)


# What is required?
Python 3.5 or greater.

## [Dependencies](requirements.txt)
- [pycdlib](https://pypi.org/project/pycdlib/)
- [psutil](https://pypi.org/project/psutil/)
- [PySimpleGUI](https://pypi.org/project/PySimpleGUI/)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
