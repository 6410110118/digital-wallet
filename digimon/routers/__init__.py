from . import items
from . import merchants
from . import transactions
from . import wallets
from . import users
from . import authentications

def init_router(app):
    app.include_router(users.router)
    app.include_router(authentications.router)
    app.include_router(items.router)
    app.include_router(merchants.router)
    app.include_router(transactions.router)
    app.include_router(wallets.router)
    