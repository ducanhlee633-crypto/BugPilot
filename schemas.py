from pydantic import BaseModel

class Clone_repo(BaseModel):
    url:str
class Delete_folder(BaseModel):
    folder:str
class Prompt(BaseModel):
    prompt:str