
# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD
from datetime import datetime

import re
import os

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio

import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file,session



# Lista de Usuarios creados
def lista_usuariosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id, name_surname, email_user,rol, created_user FROM users WHERE email_user !='admin@admin.com' ORDER BY created_user DESC"
                cursor.execute(querySQL,)
                usuariosBD = cursor.fetchall()
        return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []


# Eliminar usuario
def eliminarUsuario(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM users WHERE id=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount

        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarUsuario : {e}")
        return []


#### CONTRATOS

# Ruta de almacenamiento de archivos PDF
basepath = os.path.abspath(os.path.dirname(__file__))
upload_dir = os.path.join(basepath, 'static', 'upload_folder')

# Asegurarse de que la carpeta existe
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Verifica si el archivo es PDF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def procesar_form_contratos(dataForm, request):
    try:
        print("Procesando datos del formulario...")

        # Conectarse a la base de datos
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                
                # Validar si se reciben todos los campos
                print(f"Formulario recibido: {dataForm}")
                
                # Inserción en tbl_contratos
                sql_contrato = ("INSERT INTO tbl_contratos "
                                "(documento, razon_social, cantidad, objeto_contractual, fecha_inicio, fecha_fin, usuario_registro) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s)")
                
                valores_contrato = (
                    dataForm['documento'], dataForm['razon_social'],
                    dataForm['valor'],  # Asegúrate de que este campo esté correcto
                    dataForm['objeto_contractual'], 
                    dataForm['date_inicio'], dataForm['date_fin'],  # Estabas usando nombres incorrectos
                    session['name_surname']
                )
                
                # Verificar si los valores son los esperados
                print(f"Valores del contrato a insertar: {valores_contrato}")
                
                cursor.execute(sql_contrato, valores_contrato)
                conexion_MySQLdb.commit()
                id_contrato = cursor.lastrowid  # Obtenemos el id del contrato recién insertado
                print(f"Contrato insertado con id {id_contrato}")

                # Procesar los archivos PDF subidos
                if 'documentos_pdf' in request.files:
                    documentos_pdf = request.files.getlist('documentos_pdf')
                    print(f"Archivos subidos: {[doc.filename for doc in documentos_pdf]}")

                    for documento in documentos_pdf:
                        if documento and allowed_file(documento.filename):
                            # Agregar marca de tiempo al nombre del archivo para evitar sobrescrituras
                            filename = secure_filename(documento.filename)
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            filename_with_timestamp = f"{timestamp}_{filename}"

                            # Guardar el archivo en el servidor
                            file_path = os.path.join(upload_dir, filename_with_timestamp)
                            documento.save(file_path)
                            print(f"Archivo guardado en: {file_path}")

                            # Insertar información del archivo en tbl_documentos
                            sql_documento = ("INSERT INTO tbl_documentos "
                                                "(id_contrato, nombre_documento, usuario_registro) "
                                                "VALUES (%s, %s, %s)")
                            valores_documento = (id_contrato, filename_with_timestamp, session['name_surname'])
                            cursor.execute(sql_documento, valores_documento)

                conexion_MySQLdb.commit()
                return "Registro exitoso", 200

    except Exception as e:
        print(f"Error: {str(e)}")  # Agregar depuración
        return f'Se produjo un error en procesar_form_contratos: {str(e)}', 500
    
    
def obtener_proveedores():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id, documento_proveedor, razon_social FROM tbl_proveedor"
                cursor.execute(querySQL)
                return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener proveedores: {e}")
        return []    

    
    
def sql_lista_contratosBD(search_term=''):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT 
                        c.id_contrato,
                        c.documento,
                        c.razon_social,
                        c.cantidad,
                        c.objeto_contractual,
                        c.fecha_inicio,
                        c.fecha_fin,
                        c.fecha_registro
                    FROM tbl_contratos as c
                """
                params = []
                if search_term:
                    querySQL += """
                        WHERE c.razon_social LIKE %s OR c.objeto_contractual LIKE %s
                    """
                    like_term = f"%{search_term}%"
                    params.extend([like_term, like_term])
                querySQL += " ORDER BY fecha_registro DESC"
                cursor.execute(querySQL, params)
                contratosBD = cursor.fetchall()
        return contratosBD
    except Exception as e:
        print(f"Error en la función sql_lista_contratosBD: {e}")
        return None

def sql_detalles_contratosBD(id_contrato):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Obtener detalles del contrato
                querySQL = ("""
                    SELECT 
                        c.id_contrato,
                        c.documento,
                        c.razon_social,
                        c.cantidad,
                        c.objeto_contractual,
                        c.fecha_inicio,
                        c.fecha_fin,
                        DATE_FORMAT(c.fecha_registro, '%Y-%m-%d %h:%i %p') AS fecha_registro,
                        c.usuario_registro
                    FROM tbl_contratos AS c
                    WHERE id_contrato = %s
                """)
                cursor.execute(querySQL, (id_contrato,))
                contratoBD = cursor.fetchone()

                # Obtener los documentos asociados al contrato
                querySQL_docs = ("""
                    SELECT 
                        d.nombre_documento
                    FROM tbl_documentos AS d
                    WHERE d.id_contrato = %s
                """)
                cursor.execute(querySQL_docs, (id_contrato,))
                documentosBD = cursor.fetchall()

                # Agregar los documentos al resultado del contrato
                contratoBD['documentos'] = documentosBD

        return contratoBD
    except Exception as e:
        print(f"Error en la función sql_detalles_contratosBD: {e}")
        return None
    
def buscarContratoUnico(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            c.id_contrato,
                            c.documento,
                            c.razon_social,
                            c.cantidad,
                            c.objeto_contractual,
                            c.fecha_inicio,
                            c.fecha_fin,
                            c.fecha_registro,
                            c.usuario_registro
                        FROM tbl_contratos AS c
                        WHERE c.id_contrato =%s LIMIT 1
                    """)
                mycursor.execute(querySQL, (id,))
                contrato = mycursor.fetchone()
                return contrato
    except Exception as e:
        print(f"Ocurrió un error en def buscarContratoUnico: {e}")
        return []
    
import os
from werkzeug.utils import secure_filename

def procesar_actualizacion_contrato(data):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                id_contrato = data.form['id_contrato']
                documento = data.form['documento']
                razon_social = data.form['razon_social']
                objeto_contractual = data.form['objeto_contractual']
                cantidad = data.form['valor']
                fecha_inicio = data.form['fecha_inicio'] 
                fecha_fin = data.form['fecha_fin']             

                # Actualización en la tabla de contratos
                querySQL = """
                    UPDATE tbl_contratos
                    SET 
                        documento = %s,
                        razon_social = %s,
                        objeto_contractual=%s,
                        cantidad = %s,
                        fecha_inicio = %s,
                        fecha_fin= %s
                    WHERE id_contrato = %s
                """
                values = (documento, razon_social, objeto_contractual, cantidad, fecha_inicio, fecha_fin, id_contrato)
                cursor.execute(querySQL, values)
                conexion_MySQLdb.commit()

                # Procesar archivos adicionales
                if 'nuevo_archivo' in data.files:
                    nuevos_archivos = data.files.getlist('nuevo_archivo')
                    print(f"Archivos subidos: {[archivo.filename for archivo in nuevos_archivos]}")

                    for archivo in nuevos_archivos:
                        if archivo and allowed_file(archivo.filename):
                            # Agregar marca de tiempo al nombre del archivo para evitar sobrescrituras
                            filename = secure_filename(archivo.filename)
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            filename_with_timestamp = f"{timestamp}_{filename}"

                            # Guardar el archivo en el servidor
                            file_path = os.path.join(upload_dir, filename_with_timestamp)
                            archivo.save(file_path)
                            print(f"Archivo guardado en: {file_path}")

                            # Insertar información del archivo en tbl_documentos
                            queryArchivo = """
                                INSERT INTO tbl_documentos (id_contrato, nombre_documento, usuario_registro)
                                VALUES (%s, %s, %s)
                            """
                            valores_documento = (id_contrato, filename_with_timestamp, session['name_surname'])
                            cursor.execute(queryArchivo, valores_documento)

                conexion_MySQLdb.commit()
        return cursor.rowcount or []
    except Exception as e:
        print(f"Ocurrió un error en procesar_actualizar_contrato: {e}")
        return None
    
# Eliminar Contrato
def eliminarContrato(id_contrato):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_contratos WHERE id_contrato=%s"
                cursor.execute(querySQL, (id_contrato,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminar el contrato : {e}")
        return []
 

# Ruta de almacenamiento de archivos PDF
basepath = os.path.abspath(os.path.dirname(__file__))
upload_dir = os.path.join(basepath, 'static', 'upload_folder')

# Asegurarse de que la carpeta existe
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Verifica si el archivo es PDF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Ruta de almacenamiento de archivos PDF
basepath = os.path.abspath(os.path.dirname(__file__))
upload_dir = os.path.join(basepath, 'static', 'upload_folder')

# Asegurarse de que la carpeta existe
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Verifica si el archivo es PDF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def procesar_form_innovaciones(dataForm, request):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:

                sql = ("INSERT INTO tbl_innovacion (titulo_idea, fecha_inicio, descripcion_idea, espacio_problema, aspecto, roles, diseno, id_kim, implementacion, fecha_plazo, evaluacion, aprender_planear, ajustes, fecha_fin, usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

                # Obtener valores del formulario
                titulo = dataForm.get('titulo')
                fecha_inicio = dataForm.get('date_inicio')
                idea = dataForm.get('idea')
                problema = dataForm.get('problema')
                afecta = dataForm.get('afecta')
                definir_role = dataForm.get('definir_role')
                diseno = dataForm.get('diseno')
                id_kim = dataForm.get('kim')
                implementacion = dataForm.get('implementacion')
                fecha_plazo = dataForm.get('date_implementacion')
                evaluacion = dataForm.get('evaluacion')
                aprender_planear = dataForm.get('diseñar')
                ajustes = dataForm.get('ajustes')
                fecha_fin = dataForm.get('date_fin')
                usuario_registro = session.get('name_surname')

                # Convertir campos a None si están vacíos
                def empty_to_none(value):
                    return value.strip() if value and value.strip() else None

                fecha_plazo = empty_to_none(fecha_plazo)
                fecha_fin = empty_to_none(fecha_fin)
                id_kim = int(id_kim) if id_kim else None

                # Crear la tupla de valores
                valores = (
                    titulo, fecha_inicio, idea, problema, afecta, definir_role, 
                    diseno, id_kim, implementacion, fecha_plazo, evaluacion,
                    aprender_planear, ajustes, fecha_fin, usuario_registro
                )

                # Ejecutar inserción en tbl_innovacion
                cursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                id_innovacion = cursor.lastrowid
                print(f"Innovación insertada con id {id_innovacion}")

                # Procesar los archivos PDF subidos (si los hay)
                if 'documentos_pdf' in request.files:
                    documentos_pdf = request.files.getlist('documentos_pdf')
                    for documento in documentos_pdf:
                        if documento and allowed_file(documento.filename):
                            # Asegurar el nombre del archivo y agregar timestamp
                            filename = secure_filename(documento.filename)
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            filename_with_timestamp = f"{timestamp}_{filename}"

                            # Guardar archivo en el servidor
                            file_path = os.path.join(upload_dir, filename_with_timestamp)
                            documento.save(file_path)
                            print(f"Archivo guardado en: {file_path}")

                            # Insertar registro en tbl_documentos_innovacion
                            sql_documento = ("INSERT INTO tbl_documentos_innovacion (id_innovacion, nombre_documento, usuario_registro) VALUES (%s, %s, %s)")
                            valores_documento = (id_innovacion, filename_with_timestamp, usuario_registro)
                            cursor.execute(sql_documento, valores_documento)
                            conexion_MySQLdb.commit()
                        else:
                            print(f"Archivo no permitido o inválido: {documento.filename}")

                return "Registro exitoso", 200

    except Exception as e:
        print(f"Error en procesar_form_innovaciones: {str(e)}")
        return f'Se produjo un error en procesar_form_innovaciones: {str(e)}', 500

    
    # Lista de Innovación
def sql_lista_innovacionesBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT 
                        `id_innovacion`,
                        `titulo_idea`,
                        `fecha_inicio`,
                        `descripcion_idea` ,
                        `espacio_problema`,
                        `aspecto`,
                        `roles`,
                        `diseno`,
                        `id_kim`,
                        `implementacion`,
                        `fecha_plazo`,
                        `evaluacion`,
                        `aprender_planear`,
                        `ajustes`,
                        `fecha_fin`,
                        `fecha_registro`,
                        `usuario_registro`
                        FROM bd_contratos.tbl_innovacion
                        ORDER BY id_innovacion DESC
                    """
                cursor.execute(querySQL)
                innovacionBD = cursor.fetchall()
        return innovacionBD
    except Exception as e:
        print(f"Error en la función sql_lista_innovacionesBD: {e}")
        return None
    
    
def sql_detalles_innovacionesBD(id_innovacion):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        i.id_innovacion,
                        i.titulo_idea,
                        i.fecha_inicio,
                        i.descripcion_idea,
                        i.espacio_problema,
                        i.aspecto,
                        i.roles,
                        i.diseno,
                        i.id_kim,
                        K.nombre_kim,
                        i.implementacion,
                        i.fecha_plazo,
                        i.evaluacion,
                        i.aprender_planear,
                        i.ajustes,
                        i.fecha_fin,
                        DATE_FORMAT(i.fecha_registro, '%Y-%m-%d %h:%i %p') AS fecha_registro,
                        i.usuario_registro
                    FROM bd_contratos.tbl_innovacion AS i
                    LEFT JOIN tbl_kim AS K ON K.id_kim = i.id_kim
                    WHERE i.id_innovacion = %s
                """)
                cursor.execute(querySQL, (id_innovacion,))
                innovacionBD = cursor.fetchone()
                print(innovacionBD) 
        return innovacionBD
    except Exception as e:
        print(f"Error en la función sql_detalles_innovacionesBD: {e}")
        return None
    
def actualizar_innovacionBD(
    id_innovacion,
    titulo_idea,
    fecha_inicio,
    descripcion_idea,
    espacio_problema,
    aspecto,
    roles,
    diseno,
    id_kim,
    implementacion,
    fecha_plazo,
    evaluacion,
    aprender_planear,
    ajustes,
    fecha_fin
):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                querySQL = """
                    UPDATE bd_contratos.tbl_innovacion
                    SET 
                        titulo_idea = %s,
                        fecha_inicio = %s,
                        descripcion_idea = %s,
                        espacio_problema = %s,
                        aspecto = %s,
                        roles = %s,
                        diseno = %s,
                        id_kim = %s,
                        implementacion = %s,
                        fecha_plazo = %s,
                        evaluacion = %s,
                        aprender_planear = %s,
                        ajustes = %s,
                        fecha_fin = %s
                    WHERE id_innovacion = %s
                """
                cursor.execute(querySQL, (
                    titulo_idea,
                    fecha_inicio,
                    descripcion_idea,
                    espacio_problema,
                    aspecto,
                    roles,
                    diseno,
                    id_kim,
                    implementacion,
                    fecha_plazo,
                    evaluacion,
                    aprender_planear,
                    ajustes,
                    fecha_fin,
                    id_innovacion
                ))
                conexion_MySQLdb.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar la innovación: {e}")
        return False


def obtener_documentos_innovacion(id_innovacion):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT nombre_documento
                    FROM tbl_documentos_innovacion
                    WHERE id_innovacion = %s
                """
                cursor.execute(querySQL, (id_innovacion,))
                documentos = cursor.fetchall()
        return documentos
    except Exception as e:
        print(f"Error al obtener documentos: {e}")
        return []


# Eliminar Innovación
def eliminarInnovacion(id_innovacion):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_innovacion WHERE id_innovacion=%s"
                cursor.execute(querySQL, (id_innovacion,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminar el registro : {e}")
        return []
    
    
    
## PERCEPCION
def procesar_form_percepcion(dataForm, id_innovacion):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:

                sql = ("INSERT INTO tbl_percepcion (id_innovacion, tipo, pregunta, respuesta, usuario_registro) VALUES (%s, %s, %s, %s, %s)")

                # Definir los grupos y las preguntas
                tipos_preguntas = {
                    'Espectativa de Rendimiento': {
                        'pregunta1': 'La implementación de la presente innovación digital me permitirá ser eficiente en mi desempeño laboral.',
                        'pregunta2': 'Me siento comprometido con la implementación de la innovación digital, esto me ayudará a mejorar la calidad de mi trabajo.'
                    },
                    'Expectativa de Esfuerzo': {
                        'pregunta3': 'Aprendiendo y usando el proyecto de innovación digital con todas sus características, cumpliré fácilmente mis tareas.',
                        'pregunta4': 'Me siento en satisfacción utilizando la propuesta implementada con la innovación digital y podré cumplir con todas mis tareas a tiempo'
                    },
                    'Condiciones Facilitadoras': {
                        'pregunta5': 'Cuento con los recursos necesarios para utilizar la innovación digital en implementación.',
                        'pregunta6': 'Cuento con entrenamiento suficiente para apropiar la nueva innovación digital.'
                    },
                    'Actitud para el uso de la idea de Innovación': {
                        'pregunta7': 'Tengo una actitud positiva para adoptar la implementación de la innovación digital.',
                        'pregunta8': 'Considero beneficiosa la innovación digital para mi empresa le ayudará seguir siendo más competitiva.'
                    }
                }

                # Verificar que id_innovacion es válido
                if not id_innovacion:
                    raise ValueError("No se ha seleccionado ninguna innovación.")

                # Recorrer las preguntas y almacenar sus respuestas
                for tipo, preguntas in tipos_preguntas.items():
                    for key, pregunta in preguntas.items():
                        respuesta = dataForm.get(key)
                        if respuesta:  # Solo guardar si la respuesta existe
                            valores = (
                                id_innovacion,  # ID de la innovación seleccionada
                                tipo,           # Tipo de pregunta (grupo)
                                pregunta,       # Pregunta específica
                                respuesta,      # Respuesta del usuario
                                session.get('name_surname')  # Nombre del usuario
                            )

                            print("Insertando valores:", valores)
                            cursor.execute(sql, valores)

                conexion_MySQLdb.commit()
                resultado_insert = cursor.rowcount
                print("Inserción completada con resultado:", resultado_insert)
                return resultado_insert

    except Exception as e:
        print(f'Error en procesar_form_percepcion: {e}')
        raise  # Para que Flask muestre el error en la consola y/o navegador


    # Lista de Innovación
def sql_lista_percepcionesBD(page, per_page):
    try:
        offset = (page - 1) * per_page
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Obtener el total de registros para calcular el número de páginas
                count_query = """
                    SELECT COUNT(*) as total
                    FROM bd_contratos.tbl_percepcion AS P
                    LEFT JOIN bd_contratos.tbl_innovacion AS I ON I.id_innovacion = P.id_innovacion
                """
                cursor.execute(count_query)
                total = cursor.fetchone()['total']
                
                # Consulta paginada
                querySQL = f"""
                    SELECT 
                        P.id_percepcion,
                        P.tipo, 
                        P.pregunta, 
                        P.respuesta, 
                        P.fecha_registro,
                        P.usuario_registro,
                        I.titulo_idea
                    FROM bd_contratos.tbl_percepcion AS P
                    LEFT JOIN bd_contratos.tbl_innovacion AS I ON I.id_innovacion = P.id_innovacion
                    ORDER BY fecha_registro DESC, tipo DESC, pregunta DESC
                    LIMIT {per_page} OFFSET {offset}
                """
                cursor.execute(querySQL)
                percepcionBD = cursor.fetchall()
        return percepcionBD, total
    except Exception as e:
        print(f"Error en la función sql_lista_percepcionesBD: {e}")
        return None, 0


def eliminarPercepcion(id_percepcion):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_percepcion WHERE id_percepcion=%s"
                cursor.execute(querySQL, (id_percepcion,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminar el registro : {e}")
        return []  
    
def obtener_innovaciones():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT 
                        id_innovacion,
                        titulo_idea
                    FROM bd_contratos.tbl_innovacion
                """
                cursor.execute(querySQL)
                innovaciones = cursor.fetchall()
        return innovaciones
    except Exception as e:
        print(f"Error al obtener innovaciones: {e}")
        return []
    