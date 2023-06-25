from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Request
from datetime import datetime
import mysql.connector

app = FastAPI()

mydb = mysql.connector.connect(
  host="localhost",
  user="sequser",
  password="1234",
  database="seq"
)
cursor = mydb.cursor()

class vm_seq(BaseModel):
    vmname: str


# Get all servers
@app.get("/listseq")
def get_all_sequences():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM mysequence")
    result = cursor.fetchall()
    return {"sequences": result}

# Get an servers by ID
@app.get("/seqid/{id}")
def get_seq_is(id: int):
    cursor = mydb.cursor()
    cursor.execute(f"SELECT * FROM mysequence WHERE id = {id}")
    result = cursor.fetchone()
    return {"sequence": result}

@app.post("/addseq")
def add_seq(vmname: vm_seq, request: Request):
    cursor = mydb.cursor()
    sql = "INSERT INTO mysequence (vmname, client_ip, timestamp) VALUES (%s, %s, %s)"
    data = (vmname.vmname, request.client.host, datetime.now())
    cursor.execute(sql, data)
    mydb.commit()
    item_id = cursor.lastrowid

    # Append item_id with 4 leading zeros to vmname
    updated_vmname = f"{vmname.vmname}{str(item_id).zfill(4)}"
    update_query = "UPDATE mysequence SET vmname = %s WHERE id = %s"
    cursor.execute(update_query, (updated_vmname, item_id))
    mydb.commit()

    select_query = "SELECT * FROM mysequence WHERE id = %s"
    cursor.execute(select_query, (item_id,))
    inserted_item = cursor.fetchone()
    
    client_ip = request.client.host
    response = {
        "id": inserted_item[0],
        "vmname": inserted_item[1],
        "client_ip": client_ip,
        "timestamp": inserted_item[3]
    }

    return response

