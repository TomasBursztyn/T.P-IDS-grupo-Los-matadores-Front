from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import requests
import json

FRONTEND_PORT = 5000
BACKEND_PORT = 4000
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}/"

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/reservar_habitacion", methods=["GET", "POST"])
def reservar_habitacion():
    # puse las reservas en una lista de diccionarios, cada posicion es un
    # diccionario que contiene la reserva

    if request.method == "POST":

        nombre = request.form.get("nombre")
        dni = request.form.get("dni")
        email = request.form.get("email")
        telefono = request.form.get("telefono")
        fecha_inicio = request.form.get("inicio_fecha")
        fecha_fin = request.form.get("fin_fecha")
        tipo_habitacion = request.form.get("tipo_habitacion")

        tabla_personas = {
            "nombre_persona": nombre,
            "dni_persona": dni,
            "email_persona": email,
            "telefono_persona": telefono
        }
        
        #poner el port de tu api
        info_cliente_json = requests.get(f"{BACKEND_URL}/clientes_dni/{dni}")
        aux = str(info_cliente_json)

        if aux == "<Response [404]>":
            requests.post(f"{BACKEND_URL}/cargar_clientes", json=tabla_personas)
            info_cliente_json = requests.get(f"{BACKEND_URL}/clientes_dni/{dni}") 

        info_cliente = info_cliente_json.json()

        id_cliente = info_cliente["id_persona"]

        tabla_reservas = {
            "fecha_inicio": fecha_inicio,
            "fecha_salida": fecha_fin,
            "tipo_habitacion": tipo_habitacion,
            "id_personas": id_cliente,
            "id_habitaciones": 2,
        }

        requests.post(f"{BACKEND_URL}/cargar_reserva", json=tabla_reservas) #poner el puerto de tu api

        # luego habria que aca hacer un llamado a la api enviando datos_reserva
        return reservas(dni)

    return render_template("reservar.html")
    # return render_template("reservar_habitacion.html")


@app.route("/contacto", methods=["GET","POST"])
def contact():
    nombre = request.form.get("contacto_nombre")
    email = request.form.get("contacto_email")
    mensaje = request.form.get("contacto_mensaje")

    datos_contacto: dict = {
       "contacto_nombre": nombre,
        "contacto_email": email,
        "contacto_mensaje": mensaje,
    }

    print(f"en /contacto datos_contacto = {datos_contacto}")
    return render_template("contact.html")


@app.route("/habitaciones")
def hotel():
    return render_template("habitaciones.html")


@app.route("/servicios")
def services():
    return render_template("servicios.html")

@app.route("/reservas/<id_reserva>/<dni>", methods=["POST"])
def eliminar_reserva(id_reserva, dni):
    requests.delete(f"{BACKEND_URL}/reservas/{id_reserva}")
    return reservas(dni)

@app.route("/reservas", methods=["GET", "POST"])
def reservas(dni=None):
    if not dni:
        dni = request.form.get("dni_reserva")

    res = requests.get(f"{BACKEND_URL}/reserva_dni/{dni}")
    reservas = res.json()

    if reservas == []:
        return render_template("mostrar_reservas.html", reservas=reservas)
    
    for reserva in reservas:
        res2 = requests.get(f"{BACKEND_URL}/habitacion/{reserva['id_habitaciones']}")
        reservas2 = res2.json()
        reserva["tipo_habitacion"] = reservas2["tipo_habitacion"]
        reserva["cantidad_personas"] = reservas2["cantidad_personas"]
        reserva["dni_persona"] = dni

    return render_template("mostrar_reservas.html", reservas=reservas)


@app.route("/reservar", methods=["GET", "POST"])
def reservar():
    # puse las reservas en una lista de diccionarios, cada posicion es un
    # diccionario que contiene la reserva

    if request.method == "POST":
        cantidad_personas = request.form.get("cantidad_personas")
        fecha_inicio = request.form.get("inicio_fecha")
        fecha_fin = request.form.get("fin_fecha")

        fecha_actual = str(date.today())
        if (fecha_inicio < fecha_actual) or (fecha_fin < fecha_actual) or (fecha_fin < fecha_inicio):
            chequear = True
            return render_template("reservar.html", chequear=chequear)

        reserva = {
            "cantidad_personas": cantidad_personas,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        }

        habitaciones_ocupadas_json = requests.get(f"{BACKEND_URL}/mostrar_reservas/{fecha_inicio}/{fecha_fin}", json=reserva)
        habitaciones_ocupadas = habitaciones_ocupadas_json.json()

        id_habitaciones_ocupadas = []

        for habitacion in habitaciones_ocupadas:
            id_habitaciones_ocupadas.append(habitacion["id_habitaciones"])
        
        habitaciones_totales_json = requests.get(f"{BACKEND_URL}/mostrar_habitaciones", json=reserva)
        habitaciones_totales = habitaciones_totales_json.json()

        habitaciones_disponibles = []

        for habitacion in habitaciones_totales:
            if habitacion["id_habitacion"] not in id_habitaciones_ocupadas and habitacion["cantidad_personas"] >= int(cantidad_personas):
                habitaciones_disponibles.append(habitacion)



        # luego habria que aca hacer un llamado a la api enviando datos_reserva
        return render_template("disponibilidad.html", habitaciones=habitaciones_disponibles, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

    return render_template("reservar.html")


@app.route("/disponibilidad/<fecha_inicio>/<fecha_fin>/<cantidad_personas>/<tipo_habitacion>")
def disponibilidad(fecha_inicio, fecha_fin, cantidad_personas, tipo_habitacion):

    reserva = {
        "cantidad_personas": cantidad_personas,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "tipo_habitacion": tipo_habitacion,
    }


    return render_template("reservar_habitacion.html", reserva=reserva) 


@app.errorhandler(404)
def page_not_found_error(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=FRONTEND_PORT, debug=True)
