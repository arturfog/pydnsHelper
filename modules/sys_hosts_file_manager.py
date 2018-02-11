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

    def update_system_host(self):
        pass

    def restore_hosts_from_backup(self):
        pass

    def set_default_hosts(self):
        pass

    @staticmethod
    def get_file_sha256(path: str) -> str:
        import hashlib
        sha256 = hashlib.sha256()
        sha256.update(open(path).read())
        return sha256.hexdigest()

    @staticmethod
    def check_system_hosts():
        SystemHostFileManager.get_file_sha256(SystemHostFileManager.get_hosts_path())

