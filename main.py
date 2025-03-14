from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from codecs import decode
import chardet
from datetime import datetime
import os
import uvicorn

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
        encoding = chardet.detect(contents)['encoding']

        try:
            answer = reformat(contents.decode(encoding=encoding, errors="replace"))
            return StreamingResponse(
                answer,
                media_type="text/plain",
                headers={
                    "Content-Disposition": "attachment;filename="+ file.filename + "-arreglado.txt"
                }        
            )
        except Exception as error:
            return templates.TemplateResponse("index.html", {"flash": str(error), "request": request})


async def reformat(text:str):
    wholefile = text.splitlines()
    header = wholefile[0:14]

    # yield "\r\n".join(header)
    
    body=wholefile[1:]
    yield "\n" * 14
    yield "Fecha Mvto              Fecha Valo                                  Monto    Referencia            Concepto                                               Saldo\n"
    elements =[]
    for index, line in enumerate(body):
        chunks = list(map(str.strip, line.split("\t")))
        fecha = chunks[2]
        data={
            'index': index,
            'date': datetime.strptime(fecha, "%d/%m/%Y"),
            'fechaMvto' : fecha,
            'fechaValor' : fecha,
            'monto' : chunks[3],
            'referencia' : chunks[4], # nunmero de comporbante
            'concepto' : chunks[5],  # descripcion
            'saldo' : chunks[6],
        }
        elements.append(data)

    elements.sort(key=lambda x: (x['date'], x['index']))

    for data in elements:    
        answer = f"{data['fechaMvto']:>10.10}"
        answer += f"{data['fechaValor']:>24.10}"
        answer += f"{data['monto']:>39.30}"
        answer += f"{data['referencia']:>14.13}            "
        answer += f"{data['concepto']:39.39}"
        answer += f"{data['saldo']:>21.21}\r\n"
        yield answer



if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Cloud Run establece PORT=8080
    uvicorn.run(app, host="0.0.0.0", port=port)