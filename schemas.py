from pydantic import BaseModel

class Clone_repo(BaseModel):
    url:str
class List_files(BaseModel):
    file:str