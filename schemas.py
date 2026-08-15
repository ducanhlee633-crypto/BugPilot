from pydantic import BaseModel

class Clone_repo(BaseModel):
    url:str
class Prompt(BaseModel):
    prompt:str