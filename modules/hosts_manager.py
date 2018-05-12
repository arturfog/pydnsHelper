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

import os
import re
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Host(Base):
    __tablename__ = 'host'

    id = Column(Integer, primary_key=True)
    url = Column(String(250), nullable=False, unique=True)
    ip = Column(String(64), nullable=False)
    ttl = Column(Integer, nullable=False)
    comment = Column(String(250))


class HostsManager:

    def __init__(self):
        self.eng = None
        self.conn = None
        self.session = None

    def create_db(self, path):
        print("Creating db ... " + path)
        self.eng = create_engine("sqlite:///" + path, echo=False)
        # create all tables
        Base.metadata.create_all(self.eng)
        # connect to db
        self.conn = self.eng.connect()

    def open_db(self, path):
        if os.path.isfile(path) is False:
            self.create_db(path)
        else:
            self.eng = create_engine("sqlite:///" + path, echo=False)
            self.conn = self.eng.connect()

        db_session = sessionmaker(bind=self.eng)
        self.session = db_session()

    def block_site(self, url: str):
        self.remove_site(url)
        self.add_site(url=url, ttl=999)

    def unblock_site(self, url: str):
        self.remove_site(url)

    def get_ip(self, url: str):
        instance = self.session.query(Host).filter_by(url=url).first()
        if instance:
            return instance.ip
        else:
            return None

    def add_site(self, url: str, comment: str="", ttl: int=60, ip: str='0.0.0.0'):
        if url == "" or url == "0.0.0.0":
            return

        new_host = Host(ip=ip, url=url, ttl=ttl, comment=comment)
        self.session.add(new_host)

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()

    def remove_site(self, url: str):
        host = self.session.query(Host).filter(Host.url == url).one()
        self.session.remove(host)
        self.session.commit()

    def import_host_files(self, path: str):
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        for file in onlyfiles:
            with open(join(path, file), "r") as hosts_file:
                for line in hosts_file:
                    self.add_imported_entry(line)
            self.session.commit()

    def add_imported_entry(self, line: str):
        line = line.strip()
        if line.startswith("#"):
            return

        line = re.sub('[\t+]', '', line)
        line = re.sub('#', ' ', line)

        columns = line.split(' ')
        columns_nr = len(columns)
        url = columns[1] if columns_nr > 1 else None

        if url is not None:
            if self.get_ip(url) is not None:
                return

        if columns_nr > 2:
            self.add_site(url=url, comment=' '.join(columns[2:columns_nr]), ttl=999)
        elif columns_nr > 1:
            self.add_site(url, ttl=999)

    def get_session(self):
        return self.session

    def monitor_ttl(self):
        pass

    @staticmethod
    def generate_host_file(session, output_path: str):
        hosts = session.query(Host)
        with open(output_path, "w") as hosts_file:
            for host in hosts:
                hosts_file.write(host.ip + " " + host.url + "\n")
