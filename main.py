from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datos import guardar_expediente
from logica import validar_dni, buscar_expediente, ordenar_expedientes

app = FastAPI(
    title="Mesa de Partes Digital",
    description="API desarrollada para avance desafio de Fundamentos de Programacion - Semana07 - Grupo 01",
    version="1.0.0"
)

class ExpedienteRequest(BaseModel):
    codigo: str = Field(..., example="EXP-001")
    dni: str = Field(..., example="12345678")
    nombreCompleto: str = Field(..., example="Miguel Deza Montoya")
    tramite: str = Field(..., example="Solicitud de Licencia")

@app.post("/expedientes/", summary="Registrar nuevo expediente")
def registrar(exp: ExpedienteRequest):
    #Verificar formato dni y dar error con mensaje si no
    if not validar_dni(exp.dni):
        raise HTTPException(status_code=400, detail="DNI invalido. Debe contener 8 digitos numericos")

    #Verificar si ya existe el codigo
    if buscar_expediente(exp.codigo):
        raise HTTPException(status_code=400, detail="El codigo de expediente ya existe. Inserte uno nuevo")

    guardar_expediente(exp.codigo, exp.dni, exp.nombreCompleto, exp.tramite)
    return {"mensaje": "Expediente registrado y almacenado correctamente. ", "datos":exp}

@app.get("/expedientes/", summary="Listar y ordenar expedientes")
def listar():
    expedientes_ordenados = ordenar_expedientes()
    return {"total": len(expedientes_ordenados), "expedientes": expedientes_ordenados}

@app.get("/expedientes/{codigo}", summary="Consultar expediente por codigo")
def consultar(codigo: str):
    resultado = buscar_expediente(codigo)
    if not resultado:
        raise HTTPException(status_code=404, detail="Expediente no encontrado. Verifique que el codigo ingresado existe")
    return resultado