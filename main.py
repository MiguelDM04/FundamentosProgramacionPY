from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datos import guardar_expediente
from logica import validar_dni, buscar_expediente, ordenar_expedientes, actualizar_expediente, desactivar_expediente

app = FastAPI(
    title="Mesa de Partes Digital",
    description="API desarrollada para avance desafio de Fundamentos de Programacion - Semana07 - Grupo 01",
    version="1.0.1"
)

class ExpedienteRequest(BaseModel):
    codigo: str = Field(..., example="EXP-001")
    dni: str = Field(..., example="12345678")
    nombreCompleto: str = Field(..., example="Miguel Deza Montoya")
    tramite: str = Field(..., example="Solicitud de Licencia")

class ExpedienteUpdateRequest(BaseModel):
    dni: str = Field(..., example="12345876")
    nombreCompleto: str = Field(..., example="Miguel Deza Castillo")
    tramite: str = Field(..., example="Ampliacion de Licencia")

@app.post("/expedientes/", summary="Registrar nuevo expediente")
def registrar(exp: ExpedienteRequest):
    #Verificar formato dni y dar error con mensaje si no
    if not validar_dni(exp.dni):
        raise HTTPException(status_code=400, detail="DNI invalido. Debe contener 8 digitos numericos")

    #Verificar si ya existe el codigo
    if buscar_expediente(exp.codigo):
        raise HTTPException(status_code=400, detail="El codigo de expediente ya existe. Inserte uno nuevo")

    guardar_expediente(exp.codigo, exp.dni, exp.nombreCompleto, exp.tramite, "True")
    return {"mensaje": "Expediente registrado y almacenado correctamente. ", "datos":exp}

@app.get("/expedientes/", summary="Listar y ordenar expedientes")
def listar():
    expedientes_ordenados = ordenar_expedientes()
    return {"total": len(expedientes_ordenados), "expedientes": expedientes_ordenados}

@app.get("/expedientes/{codigo}", summary="Consultar expediente por codigo")
def consultar(codigo: str):
    resultado = buscar_expediente(codigo)
    if not resultado:
        raise HTTPException(status_code=404, detail="Expediente Activo no encontrado. Verifique que el codigo ingresado existe")
    return resultado

@app.put("/expedientes/{codigo}", summary="Actualizar expediente por codigo")
def actualizar(codigo: str, exp_upd: ExpedienteUpdateRequest):
    exito = actualizar_expediente(codigo, exp_upd.dni, exp_upd.nombreCompleto, exp_upd.tramite)
    if not exito:
        raise HTTPException(status_code=404, detail="El expediente debe de existir o estar activo para actualizarse.")
    return {"mensaje": f"Expediente {codigo} actualizado correctamente"}

@app.delete("/expedientes/{codigo}", summary="Eliminar/Desactivar expediente")
def eliminar(codigo: str):
    exito = desactivar_expediente(codigo)
    if not exito:
        raise HTTPException(status_code=404, detail="No se pudo eliminar. El expediente es inexistente o no esta activado")
    return {"mensaje": f"Expediente {codigo} eliminado correctamente"}

