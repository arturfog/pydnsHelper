# Copyright (C) 2018  Artur Fogiel
# This file is part of pyDNSHelper.
#
# pyDNSHelper is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyDNSHelper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyDNSHelper.  If not, see <http://www.gnu.org/licenses/>.
import platform
import shutil
import os
import datetime


class SystemHostFileManager:
    @staticmethod
    def detect_os() -> str:
        return platform.system()

    @staticmethod
    def get_date_for_backup() -> str:
        now = datetime.datetime.now()
        date_str = str(now.day) + '_' + str(now.month) + '_' + str(now.year)

        return date_str

    @staticmethod
    def get_hosts_path() -> str:
        if SystemHostFileManager.detect_os() == 'Linux':
            return '/etc/hosts'
        elif SystemHostFileManager.detect_os() == 'Darwin':
            return '/etc/hosts'
        elif SystemHostFileManager.detect_os() == 'Windows':
            return 'C:\Windows\system32\drivers\etc\hosts'

        return None

    @staticmethod
    def backup_current_host() -> None:
        shutil.copy2(SystemHostFileManager.get_hosts_path(),
                     os.getcwd() + '/backups/hosts_' + SystemHostFileManager.get_date_for_backup() + '.bak')

    @staticmethod
    def get_file_sha256(path: str) -> str:
        import hashlib
        sha256 = hashlib.sha256()
        sha256.update(open(path).read())
        return sha256.hexdigest()

    @staticmethod
    def check_system_hosts():
        SystemHostFileManager.get_file_sha256(SystemHostFileManager.get_hosts_path())

