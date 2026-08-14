from fastapi import FastAPI
import os
import requests
from dotenv import load_dotenv
import json 
from tools.clone_repo import clone_repo
from schemas import Clone_repo,List_files,Read_file
from tools.list_files import call_tool as call_tool_list
from tools.read_file import call_tool as call_tool_read_file

app = FastAPI()



#clone repo
@app.post("/clone_repo")
def clone_repo_endpoint(url:Clone_repo):
    result = clone_repo(url.url)
    return {"message":result}

@app.post("/list_files")
def list_files_endpoint(prompt:List_files):
    result = call_tool_list(prompt.folder)
    return result

@app.post("/read_file")
def read_file_endpoint(prompt:Read_file):
    result = call_tool_read_file(prompt.file)
    return result