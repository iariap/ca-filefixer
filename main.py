from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from codecs import decode

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_root(request:Request):
    return templates.TemplateResponse("index.html", {"request":request})

@app.post("/uploadFile")
async def uploadFile(request: Request, file: UploadFile=None):
    if not file:
        return templates.TemplateResponse("index.html", {"flash": "Falto indicar el archivo", "request": request})
    else:
        contents=await file.read()
        answer = reformat(decode(contents))
        return StreamingResponse(
            answer,
            media_type="text/plain",
            headers={
                "Content-Disposition": "attachment;filename="+ file.filename + "-arreglado.txt"
            }        
        )

async def reformat(text:str):
    wholefile = text.splitlines()
    header = wholefile[0:14]

    yield "\r\n".join(header)
    
    body=wholefile[14:]
    for line in body:
        data={
            'fechaMvto' : str(line[0:11].strip()),
            'fechaValor' : line[30:41].strip(),
            'monto' : line[41:90].strip(),
            'referencia' : line[90:104].strip(),
            'concepto' : line[120:161].strip(),
            'saldo' : line[162:191].strip(),
        }    
        answer = f"{data['fechaMvto']:>10.10}"
        answer += f"{data['fechaValor']:>24.10}"
        answer += f"{data['monto']:>39.30}"
        answer += f"{data['referencia']:>14.13}            "
        answer += f"{data['concepto']:39.39}"
        answer += f"{data['saldo']:>21.21}\r\n"
        yield answer


