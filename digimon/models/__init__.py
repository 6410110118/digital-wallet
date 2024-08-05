from sqlmodel import SQLModel, Session , create_engine



from .items import *
from .merchants import *
from .transactions import *
from.wallets import *

connect_args = {}

engine = create_engine(
    "postgresql+pg8000://postgres:123456@localhost/digimondb",
    echo=True,
    connect_args=connect_args,
)


def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session