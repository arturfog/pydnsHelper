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

## Docker

```sh
# 1. build docker image
sudo docker build -t arturfog/pydnshelper .

# 2. run image
sudo docker run -it -p 8000:8000/tcp -p 8000:8000/udp -p 5053:5053/udp arturfog/pydnshelper /bin/bash

# 3. go to pyDNSHelper directory
cd /pyDNSHelper

# 4. run first_start.sh script (it will created database and admin user)
./first_start.sh

# 5. verify app is working by going to http://$DOCKER_CONTAINER_IP:8000/webui/

docker container ip can be checked with 'docker inspect $containerID` command

-------------------------------------------------------------------------------------

Next time you want to use pyDNSHelper following steps are needed

# 1. start container 
sudo docker start CONTAINER_NAME ie. sudo docker start hopeful_hawking

it's also possible to enter shell of the container:
sudo docker exec -it CONTAINER_NAME bash
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
