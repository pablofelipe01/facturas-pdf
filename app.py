import io
import re
from flask import Flask, request, jsonify, render_template
from pdfminer.high_level import extract_text

app = Flask(__name__)

def extract_pdf_text(pdf_file):
    """
    Convierte el archivo subido a un objeto BytesIO y extrae el texto del PDF usando pdfminer.six.
    """
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)  # Resetea el puntero por si se necesita leer de nuevo
    pdf_stream = io.BytesIO(pdf_bytes)
    text = extract_text(pdf_stream)
    return text

def extract_invoice_data(text):
    """
    Ejemplo de función para extraer datos puntuales del texto.
    Puedes ajustar las expresiones regulares según el formato de tus facturas.
    """
    invoice_number_match = re.search(r"Factura:\s*(\S+)", text)
    date_match = re.search(r"Fecha:\s*([\d/-]+)", text)
    total_match = re.search(r"Total:\s*([\d.,]+)", text)
    
    return {
        "invoice_number": invoice_number_match.group(1) if invoice_number_match else None,
        "date": date_match.group(1) if date_match else None,
        "total": total_match.group(1) if total_match else None,
        "full_text": text  # Opcional, para ver todo el contenido extraído
    }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'pdf_file' not in request.files:
            return jsonify({"error": "No se ha subido ningún archivo"}), 400

        file = request.files["pdf_file"]
        if file.filename == "":
            return jsonify({"error": "Archivo no seleccionado"}), 400

        try:
            extracted_text = extract_pdf_text(file)
            data = extract_invoice_data(extracted_text)
            return jsonify({
                "status": "ok",
                "data": data
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
