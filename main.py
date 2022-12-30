from fastapi import FastAPI
from Social_box import models
from Social_box.database import engine
from Social_box.routers import post, user, authentication, profile
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(engine)

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(profile.router)

authentication.server()