# MultiBootUsb
![](https://img.shields.io/github/issues/Konrad-Ziarko/MultiBootUsb.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/258e003beaa444a3babd651f89086f26)](https://www.codacy.com/manual/Konrad-Ziarko/MultiBootUsb?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Konrad-Ziarko/MultiBootUsb&amp;utm_campaign=Badge_Grade)
![](https://img.shields.io/github/license/Konrad-Ziarko/MultiBootUsb.svg)

GUI application for quickly adding boot entries on MultiBoot USB devices

# Disclaimer
Entries were written for RHEL/CentOs, minor changes may be needed to run properly under Debian or other distros.

## Build from source
*Run [script](installer/installer.py) stored in installer folder*

# Usage
1. Select desired removable drive from the list
2. Click 'Add boot entries' button
3. Follow popup windows to finish the process

![alt text](docs/images/screen1.png)


# What is required?
Python 3.5 or greater.

## [Dependencies](requirements.txt)
- [psutil](https://pypi.org/project/psutil/)
- [PySimpleGUI](https://pypi.org/project/PySimpleGUI/)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
