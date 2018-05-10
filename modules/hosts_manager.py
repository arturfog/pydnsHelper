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
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Host(Base):
    __tablename__ = 'host'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    url = Column(String(250), nullable=False)
    ip = Column(String(64), nullable=False)
    comment = Column(String(250))


class HostsManager:

    def __init__(self):
        self.eng = None
        self.conn = None
        self.session = None

    def create_db(self, path):
        self.eng = create_engine("sqlite://" + path)
        # create all tables
        Base.metadata.create_all(self.eng)
        # connect to db
        self.conn = self.eng.connect()

    def open_db(self, path):
        if os.path.isfile(path) is False:
            self.create_db(path)

        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()

    def block_microsoft_services(self):
        pass

    def unblock_microsoft_services(self):
        pass

    def block_site(self, url):
        pass

    def unblock_site(self, url):
        pass

    def add_site(self, url, comment):
        new_host = Host(url=url, comment=comment)
        self.session.add(new_host)
        self.session.commit()

    def remove_site(self, url):
        host = self.session.query(Host).filter(Host.url == url).one()
        self.session.remove(host)
        self.session.commit()

    def clean_host_file(self, path):
        pass

    def import_host_file(self, path):
        pass

    def generate_host_file(self, output_path):
        pass
