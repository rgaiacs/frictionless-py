from .server import server


@server.get("/validate")
def server_validate():
    return {"Hello": "World"}