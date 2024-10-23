from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify, Blueprint
from mysql.connector.errors import Error
from flask import send_from_directory

# Importando cenexión a BD
from controllers.funciones_home import *

PATH_URL = "public/empleados"


@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        resp_usuariosBD = lista_usuariosBD()
        return render_template('public/usuarios/lista_usuarios.html', resp_usuariosBD=resp_usuariosBD)
    else:
        return redirect(url_for('inicioCpanel'))


@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))


#### CONTRATOS
@app.route('/registrar-contratos', methods=['GET', 'POST'])
def viewFormContratos():
    try:
        if request.method == 'POST':
            print(request.form)  # Imprimir los datos del formulario para depuración
            print(request.files)  # Imprimir los archivos subidos para depuración

            # Procesar el formulario y archivos
            resultado, status_code = procesar_form_contratos(request.form, request)
            if status_code == 200:
                flash('Registro exitoso', 'success')
                return redirect(url_for('lista_contratos'))  # Redirigir a lista_contratos después de éxito
            else:
                flash(resultado, 'error')
                return redirect(url_for('viewFormContratos'))
        else:
            if 'conectado' in session:
                return render_template('public/contratos/form_contratos.html')
            else:
                flash('Primero debes iniciar sesión.', 'error')
                return redirect(url_for('inicio'))
    except Exception as e:
        print(f"Error en la solicitud: {str(e)}")
        return "400 Bad Request", 400
    
    
@app.route('/lista-de-contratos', methods=['GET'])
def lista_contratos():
    if 'conectado' in session:
        search_term = request.args.get('search', '')
        contratos = sql_lista_contratosBD(search_term)
        return render_template('public/contratos/lista_contratos.html', contratos=contratos)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route("/detalles-contrato/<string:id_contrato>", methods=['GET'])
def detalleContrato(id_contrato=None):
    if 'conectado' in session:
        if id_contrato is None:
            return redirect(url_for('inicio'))
        else:
            detalle_contrato = sql_detalles_contratosBD(id_contrato) or []
            return render_template('public/contratos/detalles_contratos.html', detalle_contrato=detalle_contrato)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route("/editar-contrato/<int:id_contrato>", methods=['GET'])
def viewEditarContrato(id_contrato=None):
    if 'conectado' in session:
        if id_contrato is None:
            return redirect(url_for('inicio'))
        else:
            respuestaContrato = sql_detalles_contratosBD(id_contrato) or []
            return render_template('public/contratos/form_contratos_update.html', respuestaContrato=respuestaContrato)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(upload_dir, filename)

# Recibir formulario para actulizar informacion de cliente
@app.route('/actualizar-contrato', methods=['POST'])
def actualizarContrato():
    print(request.form)
    try:
        resultData = procesar_actualizacion_contrato(request)
        if resultData:
            # Redirige a la lista de contratos si la actualización fue exitosa
            return redirect(url_for('lista_contratos'))
        else:
            # Mostrar mensaje de error si no se actualizó el contrato
            flash('No se pudo actualizar el contrato.', 'error')
            return redirect(url_for('viewEditarContrato', id_contrato=request.form['id_contrato']))
    except Exception as e:
        # Capturar cualquier otro error inesperado y mostrar mensaje
        print(f"Ocurrió un error en la actualización: {e}")
        flash('Ocurrió un error durante la actualización del contrato.', 'error')
        return redirect(url_for('viewEditarContrato', id_contrato=request.form['id_contrato']))
    
@app.route('/borrar-contrato/<int:id_contrato>', methods=['GET'])
def borrarContrato(id_contrato):
    resp = eliminarContrato(id_contrato)
    if resp:
        flash('El contrato fue eliminado correctamente', 'success')
        return redirect(url_for('lista_contratos'))
    
    


##INNOVACION
@app.route('/registrar-innovacion', methods=['GET', 'POST'])
def viewFormInnovacion():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        dataForm = request.form
        try:
            resultado, status_code = procesar_form_innovaciones(dataForm, request)
            if status_code == 200:
                flash('Innovación registrada exitosamente.', 'success')
                return redirect(url_for('lista_innovaciones'))
            else:
                flash(resultado, 'error')
        except Exception as e:
            flash(f'Error al registrar la innovación: {e}', 'error')
    
    return render_template('public/innovacion/form_innovacion.html')


@app.route('/lista-de-innovaciones', methods=['GET'])
def lista_innovaciones():
    if 'conectado' in session:
        return render_template('public/innovacion/lista_innovaciones.html', innovacion=sql_lista_innovacionesBD())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route("/detalles-innovacion/<string:id_innovacion>", methods=['GET', 'POST'])
def detalleInnovacion(id_innovacion=None):
    if 'conectado' in session:
        if id_innovacion is None:
            return redirect(url_for('inicio'))
        else:
            if request.method == 'POST':
                # Procesar los datos del formulario
                titulo_idea = request.form['titulo_idea']
                fecha_inicio = request.form['fecha_inicio'] or None
                descripcion_idea = request.form['descripcion_idea']
                espacio_problema = request.form['espacio_problema']
                aspecto = request.form['aspecto']
                roles = request.form['roles']
                estrategias = request.form['estrategias']
                diseno = request.form['diseno']
                kim = request.form['kim']
                implementacion = request.form['implementacion']
                fecha_plazo = request.form['fecha_plazo'] or None
                evaluacion = request.form['evaluacion']
                aprender_planear = request.form['aprender_planear']
                ajustes = request.form['ajustes']
                fecha_fin = request.form['fecha_fin'] or None

                # Convertir fechas vacías a None
                fecha_inicio = fecha_inicio.strip() if fecha_inicio and fecha_inicio.strip() else None
                fecha_plazo = fecha_plazo.strip() if fecha_plazo and fecha_plazo.strip() else None
                fecha_fin = fecha_fin.strip() if fecha_fin and fecha_fin.strip() else None

                # Actualizar la innovación en la base de datos
                resultado = actualizar_innovacionBD(
                    id_innovacion,
                    titulo_idea,
                    fecha_inicio,
                    descripcion_idea,
                    espacio_problema,
                    aspecto,
                    roles,
                    estrategias,
                    diseno,
                    kim,
                    implementacion,
                    fecha_plazo,
                    evaluacion,
                    aprender_planear,
                    ajustes,
                    fecha_fin
                )

                # Procesar nuevos documentos cargados
                print(f"Archivos en request.files: {request.files}")  # Depuración
                if 'nuevos_documentos' in request.files:
                    documentos_pdf = request.files.getlist('nuevos_documentos')
                    print(f"Cantidad de archivos subidos: {len(documentos_pdf)}")  # Depuración
                    for documento in documentos_pdf:
                        if documento and allowed_file(documento.filename):
                            filename = secure_filename(documento.filename)
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            filename_with_timestamp = f"{timestamp}_{filename}"
                            file_path = os.path.join(upload_dir, filename_with_timestamp)
                            documento.save(file_path)
                            print(f"Archivo guardado en: {file_path}")  # Depuración

                            # Insertar información del archivo en la base de datos
                            with connectionBD() as conexion_MySQLdb:
                                with conexion_MySQLdb.cursor() as cursor:
                                    sql_documento = ("INSERT INTO tbl_doc_innovacion "
                                                     "(id_innovacion, nombre_documento, usuario_registro) "
                                                     "VALUES (%s, %s, %s)")
                                    valores_documento = (id_innovacion, filename_with_timestamp, session['name_surname'])
                                    print(f"Valores a insertar en tbl_doc_innovacion: {valores_documento}")  # Depuración
                                    cursor.execute(sql_documento, valores_documento)
                                    conexion_MySQLdb.commit()
                        else:
                            print(f"Archivo no permitido o inválido: {documento.filename}")

                if resultado:
                    flash('Innovación actualizada correctamente.', 'success')
                else:
                    flash('Ocurrió un error al actualizar la innovación.', 'error')

                # Obtener los detalles y documentos actualizados
                detalle_innovacion = sql_detalles_innovacionesBD(id_innovacion) or []
                documentos = obtener_documentos_innovacion(id_innovacion)
                return render_template('public/innovacion/detalles_innovacion.html', detalle_innovacion=detalle_innovacion, documentos=documentos)
            else:
                detalle_innovacion = sql_detalles_innovacionesBD(id_innovacion) or []
                documentos = obtener_documentos_innovacion(id_innovacion)
                return render_template('public/innovacion/detalles_innovacion.html', detalle_innovacion=detalle_innovacion, documentos=documentos)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/borrar-innovacion/<int:id_innovacion>', methods=['GET'])
def borrarInnovacion(id_innovacion):
    print(f"Endpoint llamado con id_innovacion: {id_innovacion}")
    resp = eliminarInnovacion(id_innovacion)
    print(borrarInnovacion)
    if resp:
        flash('El registro fue eliminado correctamente', 'success')
        return redirect(url_for('lista_innovaciones'))
    
    
## PERCEPCIóN
@app.route('/registrar-percepcion', methods=['GET', 'POST'])
def viewFormPercepcion():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        dataForm = request.form
        try:
            # Obtener el id_innovacion del formulario
            id_innovacion = dataForm.get('id_innovacion')
            resultado = procesar_form_percepcion(dataForm, id_innovacion)
            if isinstance(resultado, int) and resultado > 0:
                flash('Percepción registrada exitosamente.', 'success')
                return redirect(url_for('lista_percepcion'))  # Reemplaza 'lista_percepcion' con la ruta adecuada
            else:
                flash('No se pudo registrar la percepción.', 'error')
        except Exception as e:
            flash(f'Error al registrar la percepción: {e}', 'error')
    
    # Método GET: obtener las innovaciones y renderizar el formulario
    innovaciones = obtener_innovaciones()
    return render_template('public/percepcion/form_percepcion.html', innovaciones=innovaciones)


@app.route('/lista-percepcion', methods=['GET'])
def lista_percepcion():
    if 'conectado' in session:
        page = request.args.get('page', 1, type=int)
        per_page = 15  # Número de registros por página
        percepcion, total = sql_lista_percepcionesBD(page, per_page)
        total_pages = (total + per_page - 1) // per_page  # Cálculo del número total de páginas
        return render_template('public/percepcion/lista_percepcion.html', percepcion=percepcion, page=page, total_pages=total_pages)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/borrar-percepcion/<int:id_percepcion>', methods=['GET'])
def borrarPercepcion(id_percepcion):
    print(f"Endpoint llamado con id_percepcion: {id_percepcion}")
    resp = eliminarPercepcion(id_percepcion)
    print(borrarPercepcion)
    if resp:
        flash('El registro fue eliminado correctamente', 'success')
        return redirect(url_for('lista_percepcion'))