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
            # Procesar el formulario y archivos
            resultado, status_code = procesar_form_contratos(request.form, request)
            if status_code == 200:
                flash('Registro exitoso', 'success')
                return redirect(url_for('lista_contratos'))
            else:
                flash(resultado, 'error')
                return redirect(url_for('viewFormContratos'))
        else:
            if 'conectado' in session:
                # Obtener los proveedores para el desplegable
                proveedores = obtener_proveedores()
                return render_template('public/contratos/form_contratos.html', proveedores=proveedores)
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
    else:
        # Obtener las opciones de KIM de la base de datos
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT id_kim, nombre_kim, descripcion_kim FROM tbl_kim")
                    kim_options = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching kim_options: {str(e)}")
            kim_options = []

        return render_template('public/innovacion/form_innovacion.html', kim_options=kim_options)

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
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    if id_innovacion is None:
        flash('No se proporcionó un ID de innovación válido.', 'error')
        return redirect(url_for('inicio'))

    # Obtener las opciones de KIM y temas
    kim_options = obtener_opciones_kim()
    tema_options = obtener_opciones_tema()

    if request.method == 'POST':
        try:
            # Procesar los datos del formulario
            titulo_idea = request.form.get('titulo_idea')
            fecha_inicio = request.form.get('fecha_inicio') or None
            descripcion_idea = request.form.get('descripcion_idea')
            espacio_problema = request.form.get('espacio_problema')
            aspecto = request.form.get('aspecto')
            roles = request.form.get('roles')
            diseno = request.form.get('diseno')
            id_kim = request.form.get('id_kim')
            id_tema = request.form.get('id_tema')  # Obtener el id_tema seleccionado
            implementacion = request.form.get('implementacion')
            fecha_plazo = request.form.get('fecha_plazo') or None
            evaluacion = request.form.get('evaluacion')
            aprender_planear = request.form.get('aprender_planear')
            ajustes = request.form.get('ajustes')
            fecha_fin = request.form.get('fecha_fin') or None

            # Actualizar la innovación en la base de datos
            resultado = actualizar_innovacionBD(
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
            )

            if not resultado:
                flash('Ocurrió un error al actualizar la innovación.', 'error')
                return redirect(url_for('detalleInnovacion', id_innovacion=id_innovacion))

            flash('Innovación actualizada correctamente.', 'success')

            # Procesar nuevos documentos cargados
            usuario_registro = session.get('name_surname')
            if 'nuevos_documentos' in request.files:
                documentos_pdf = request.files.getlist('nuevos_documentos')
                for documento in documentos_pdf:
                    if documento and allowed_file(documento.filename):
                        filename = secure_filename(documento.filename)
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        filename_with_timestamp = f"{timestamp}_{filename}"
                        file_path = os.path.join(upload_dir, filename_with_timestamp)
                        documento.save(file_path)

                        # Insertar el documento en la base de datos con id_tema
                        insertar_documento_innovacion(id_innovacion, filename_with_timestamp, usuario_registro, id_tema)

        except Exception as e:
            print(f"Error al procesar el formulario: {e}")
            flash('Ocurrió un error al procesar el formulario.', 'error')
            return redirect(url_for('detalleInnovacion', id_innovacion=id_innovacion))

    # Obtener los detalles y documentos actualizados
    try:
        detalle_innovacion = sql_detalles_innovacionesBD(id_innovacion) or []
        documentos = obtener_documentos_innovacion(id_innovacion)

        # Validar que los detalles se hayan obtenido
        if not detalle_innovacion:
            flash('No se encontraron detalles para esta innovación.', 'error')
            return redirect(url_for('inicio'))

        # Renderizar el formulario con los detalles
        return render_template(
            'public/innovacion/detalles_innovacion.html',
            detalle_innovacion=detalle_innovacion,
            documentos=documentos,
            kim_options=kim_options,
            tema_options=tema_options
        )

    except Exception as e:
        print(f"Error al obtener los detalles de la innovación: {e}")
        flash('Ocurrió un error al obtener los detalles de la innovación.', 'error')
        return redirect(url_for('inicio'))

def obtener_opciones_kim():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_kim, nombre_kim, descripcion_kim FROM tbl_kim"
                cursor.execute(querySQL)
                return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener opciones de KIM: {e}")
        return []
    



@app.route("/reporte-innovacion/<string:id_innovacion>", methods=['GET', 'POST'])
def reporteInnovacion(id_innovacion=None):
    if 'conectado' in session:
        if id_innovacion is None:
            return redirect(url_for('inicio'))
        else:
            # Obtener las opciones de KIM
            kim_options = obtener_opciones_kim()

            # Obtener los detalles de la innovación y los documentos asociados
            reporte_innovacion = sql_detalles_innovacionesBD(id_innovacion) or []
            documentos = obtener_documentos_innovacion(id_innovacion)

            return render_template('public/innovacion/innovacion_report.html',
                reporte_innovacion=reporte_innovacion,
                documentos=documentos,
                kim_options=kim_options
            )
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