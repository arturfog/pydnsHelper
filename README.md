# pydnsHelper
| Service | Status                                         |                                                                                 
| ------- | ---------------------------------------------- |
| Snapcraft   | [![Snap Status](https://build.snapcraft.io/badge/arturfog/pydnsHelper.svg)](https://build.snapcraft.io/user/arturfog/pydnsHelper) |
| Gitter | [![Gitter](https://badges.gitter.im/arturfog/pydnsHelper.svg)](https://gitter.im/arturfog/pydnsHelper?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge) |

Python DNS server focused on security, supporting DNSSEC and DNS over SSL (can automatically block ads and malicious websites)

![Main Window](https://github.com/arturfog/pydnsHelper/raw/master/assets/app_main.png)

## Testing

```sh
dig @localhost google.pl -p 5053
```

## Build

![ubuntu](https://github.com/arturfog/qtS3Browser/raw/master/assets/64_ubuntu_icon.png)
### Ubuntu

```sh
# 1. Setup virtualenv
./install.sh

# 2. activate virtualenv
source venv/bin/activate

# 3. install requirements
pip install -r requirements.txt

# 4. run first start script
./first_start.sh
```

## Installation

![ubuntu](https://github.com/arturfog/qts3browser/raw/master/assets/64_ubuntu_icon.png)![fedora](https://github.com/arturfog/qts3browser/raw/master/assets/64_fedora_icon.png)![arch](https://github.com/arturfog/qts3browser/raw/master/assets/64_arch_icon.png)![mint](https://github.com/arturfog/qts3browser/raw/master/assets/64_mint_icon.png)![rpi](https://github.com/arturfog/qts3browser/raw/master/assets/64_rpi_icon.png)

```sh
# note: application is still under active development (it will be soon released in experimental 'edge' channel)

snap install --edge pydnshelper
```

# Support this project
- Star GitHub repository :star:
- Create pull requests, submit bugs or suggest new features
