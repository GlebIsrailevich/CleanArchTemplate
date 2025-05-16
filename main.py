# from fastapi import FastAPI

# from infra.web.controllers.user_controller import router as user_router

# app = FastAPI()
# app.include_router(user_router)

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI

from api.routes import routers
from infra.container import Container
from infra.web.controllers.user_controller import router as user_router

# Create the container
container = Container()

# Create the database tables
container.db().create_database()

# Create FastAPI app
app = FastAPI()

# Include the user router
app.include_router(routers)
app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
