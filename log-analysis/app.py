from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
from log_analyzer import LogAnalyzer
from pdf_generator import PDFGenerator
import tempfile
import traceback

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 * 1024  # 4GB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'log', 'csv', 'json'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Error handlers to return JSON instead of HTML
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    return jsonify({'error': 'File is too large. Maximum size is 4GB.'}), 413

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Analyze the log file
            analyzer = LogAnalyzer(filepath)
            analysis_results = analyzer.analyze()
            
            # Generate PDF report
            pdf_generator = PDFGenerator(analysis_results, filename)
            pdf_path = pdf_generator.generate()
            
            
            
            # Return PDF file
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f'log_analysis_{filename.rsplit(".", 1)[0]}.pdf',
                mimetype='application/pdf'
            )
        except Exception as e:
            # Clean up on error
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            # Log the full traceback for debugging (in production, use proper logging)
            error_msg = str(e)
            if app.debug:
                error_msg += f"\nTraceback: {traceback.format_exc()}"
            return jsonify({'error': f'Error processing file: {error_msg}'}), 500
    else:
        return jsonify({'error': 'Invalid file type. Allowed types: txt, log, csv, json'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

