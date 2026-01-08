from fastapi import FastAPI
from db.session import  engine,Base  
from routers.lawyer_route import lawyerrouter
from routers.complaint_route import complaint_router
from routers.userrouter import user_router


Base.metadata.create_all(bind=engine)    



app= FastAPI()

app.include_router(lawyerrouter)
app.include_router(user_router)
app.include_router(complaint_router)



