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
    comment = Column(String(250))


class HostsManager:

    def __init__(self):
        self.eng = None
        self.conn = None
        self.session = None

    def create_db(self, path):
        self.eng = create_engine("sqlite://" + path)
        # create all tables
        Base.metadata.create_all(self.engine)
        # connect to db
        self.conn = self.eng.connect()

    def open_db(self, path):
        if os.path.isfile(path) is False:
            self.create_db(path)

        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()

    def block_google_services(self):
        pass

    def unblock_google_services(self):
        pass

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
