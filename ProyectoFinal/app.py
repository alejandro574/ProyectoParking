from flask import Flask, render_template, Response, redirect, request, session
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "tfg_parking_2026"


# =========================
# EMAIL CONFIG
# =========================
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True


app.config["MAIL_USERNAME"] = "amarfer574@ieszaidinvergeles.org"
app.config["MAIL_PASSWORD"] = "sedh xded qsve elzi"

mail = Mail(app)


# =========================
# CONFIGURACIÓN
# =========================
CONFIG = {
    "capacidad": 100,
    "confianza": 0.5
}


# =========================
# BASE DE DATOS
# =========================
def query(sql):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(sql)
    data = c.fetchall()
    conn.close()
    return data


# =========================
# GENERAR PDF
# =========================
def generar_pdf():
    archivo = "informe_parking.pdf"

    coches = query("""
        SELECT matricula, entrada, salida
        FROM coches
        ORDER BY entrada DESC
    """)

    pdf = SimpleDocTemplate(archivo, pagesize=A4)

    datos = [["MATRÍCULA", "ENTRADA", "SALIDA"]]

    for c in coches:
        salida = c[2] if c[2] else "EN PARKING"
        datos.append([c[0], c[1], salida])

    tabla = Table(datos)
    pdf.build([tabla])

    return archivo


# =========================
# LISTA NEGRA
# =========================
def cargar_lista_negra():
    try:
        with open("lista_negra.txt", "r", encoding="utf-8") as f:
            return set(x.strip().upper() for x in f.readlines())
    except:
        return set()


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        if usuario == "admin" and password == "1234":
            session["login"] = True
            return redirect("/")

        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# HOME
# =========================
@app.route("/")
def index():

    if "login" not in session:
        return redirect("/login")

    coches = query("SELECT * FROM coches ORDER BY entrada DESC")

    activos = query("""
        SELECT COUNT(*) FROM coches WHERE salida IS NULL
    """)[0][0]

    total = query("SELECT COUNT(*) FROM coches")[0][0]

    negra = cargar_lista_negra()

    alertas_negra = sum(
        1 for c in coches
        if c[2] and c[2].upper() in negra
    )

    datos_grafico = query("""
        SELECT DATE(entrada), COUNT(*)
        FROM coches
        GROUP BY DATE(entrada)
        ORDER BY DATE(entrada) DESC
        LIMIT 7
    """)

    fechas = [x[0] for x in datos_grafico][::-1]
    valores = [x[1] for x in datos_grafico][::-1]

    return render_template(
        "index.html",
        coches=coches,
        activos=activos,
        total=total,
        negra=negra,
        alertas_negra=alertas_negra,
        fechas=fechas,
        valores=valores
    )


# =========================
# CONFIG
# =========================
@app.route("/config", methods=["POST"])
def config():

    if "login" not in session:
        return redirect("/login")

    CONFIG["capacidad"] = int(request.form["capacidad"])
    CONFIG["confianza"] = float(request.form["confianza"])

    return redirect("/")


# =========================
# TXT
# =========================
@app.route("/descargar_txt")
def descargar_txt():

    matriculas = query("SELECT matricula FROM coches")
    contenido = "\n".join([m[0] for m in matriculas])

    return Response(
        contenido,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=matriculas.txt"}
    )


# =========================
# PDF
# =========================
@app.route("/descargar_pdf")
def descargar_pdf():

    archivo = generar_pdf()

    with open(archivo, "rb") as f:
        contenido = f.read()

    return Response(
        contenido,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=informe_parking.pdf"}
    )


# =========================
# 📧 ENVIAR EMAIL
# =========================
@app.route("/enviar_email")
def enviar_email():

    if "login" not in session:
        return redirect("/login")

    try:
        archivo = generar_pdf()

        msg = Message(
            subject="Informe del sistema de parking",
            sender=app.config["MAIL_USERNAME"],
            recipients=["martinfernandezalejandro6767@gmail.com"]   
        )

        msg.body = (
            "Hola,\n\n"
            "Adjunto el informe generado automáticamente del sistema de parking.\n\n"
            "Un saludo."
        )

        with open(archivo, "rb") as f:
            msg.attach(
                "informe_parking.pdf",
                "application/pdf",
                f.read()
            )

        mail.send(msg)

        return redirect("/?mail=ok")

    except Exception as e:
        print("ERROR EMAIL:", e)
        return redirect("/?mail=error")


# =========================
# INCIDENCIAS
# =========================
@app.route("/descargar_incidencias")
def descargar_incidencias():

    negra = cargar_lista_negra()

    coches = query("""
        SELECT matricula, entrada
        FROM coches
        ORDER BY entrada DESC
    """)

    incidencias = []

    for c in coches:
        if c[0] and c[0].upper() in negra:
            incidencias.append([
                f"🚨 {c[0]}",
                "DETECTADO EN LISTA NEGRA",
                c[1]
            ])

    archivo = "incidencias.pdf"
    pdf = SimpleDocTemplate(archivo, pagesize=A4)
    styles = getSampleStyleSheet()

    titulo = Paragraph("INFORME DE INCIDENCIAS", styles["Title"])

    datos = [["MATRÍCULA", "EVENTO", "FECHA"]] + incidencias

    if not incidencias:
        datos.append(["-", "SIN INCIDENCIAS", "-"])

    tabla = Table(datos)

    pdf.build([titulo, Spacer(1, 20), tabla])

    with open(archivo, "rb") as f:
        contenido = f.read()

    return Response(
        contenido,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=incidencias.pdf"}
    )


# =========================
# VACIAR BD
# =========================
@app.route("/vaciar")
def vaciar():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM coches")
    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(debug=True)