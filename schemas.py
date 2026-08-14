from pydantic import BaseModel

class Clone_repo(BaseModel):
    url:str
class List_files(BaseModel):
    folder:str

class Read_file(BaseModel):
    file : str