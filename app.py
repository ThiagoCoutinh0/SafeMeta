from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Certifique-se de criar a pasta 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Extrair metadados da imagem
    metadata = extract_metadata(filepath)
    return jsonify(metadata)

def extract_metadata(filepath):
    metadata = {}

    # Abrir a imagem com Pillow
    image = Image.open(filepath)

    # Obtendo todos os metadados disponíveis com Pillow
    exif_data = image.getexif()
    if exif_data:
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            metadata[tag_name] = value

    # Verificar e extrair informações de localização (GPS) usando piexif
    try:
        exif_dict = piexif.load(filepath)
        if 'GPS' in exif_dict:
            gps_info = exif_dict['GPS']
            gps_metadata = {}
            for key in gps_info:
                gps_metadata[key] = gps_info[key]
            metadata['GPSInfo'] = gps_metadata
    except:
        pass

    # Exemplo de outros metadados que você pode querer extrair
    metadata['filename'] = os.path.basename(filepath)
    metadata['size'] = os.path.getsize(filepath)

    # Converter valores para tipos primitivos para garantir a serialização JSON
    metadata = convert_to_primitive_types(metadata)

    return metadata

def convert_to_primitive_types(data):
    """
    Função auxiliar para converter valores em tipos primitivos para garantir a serialização JSON.
    """
    for key, value in data.items():
        if isinstance(value, bytes):
            data[key] = value.decode('utf-8', 'ignore')  # Decodifica bytes para strings UTF-8
        elif isinstance(value, tuple):
            data[key] = list(value)  # Converte tuplas para listas para garantir a serialização
        elif isinstance(value, dict):
            data[key] = convert_to_primitive_types(value)  # Recursivamente converte dicionários internos

    return data

if __name__ == '__main__':
    app.run(debug=True)

def convert_to_primitive_types(data):
    """
    Função auxiliar para converter valores em tipos primitivos para garantir a serialização JSON.
    """
    for key, value in data.items():
        if isinstance(value, bytes):
            data[key] = value.decode('utf-8', 'ignore')  # Decodifica bytes para strings UTF-8
        elif isinstance(value, tuple):
            data[key] = list(value)  # Converte tuplas para listas para garantir a serialização
        elif isinstance(value, dict):
            data[key] = convert_to_primitive_types(value)  # Recursivamente converte dicionários internos
        elif isinstance(value, int):
            data[key] = str(value)  # Converte inteiros para strings para garantir a compatibilidade

    return data

import exifread

def extract_gps_info(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
        gps_info = tags.get('GPSInfo')
        return gps_info

image_path = 'caminho/para/sua/imagem.jpg'
gps_info = extract_gps_info(image_path)
print(gps_info)
