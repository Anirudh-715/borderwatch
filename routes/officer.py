from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from models.database import get_db
from models.image_processor import analyze_image
import os
import uuid
from werkzeug.utils import secure_filename

officer_bp = Blueprint('officer', __name__, url_prefix='/officer')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_officer(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session['role'] not in ('officer', 'admin'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@officer_bp.route('/dashboard')
@require_officer
def dashboard():
    db = get_db()
    incidents = db.execute(
        """SELECT i.*, u.full_name, 
           (SELECT COUNT(*) FROM images WHERE incident_id = i.id) as image_count
           FROM incidents i JOIN users u ON i.user_id = u.id
           WHERE i.user_id = ? ORDER BY i.datetime DESC""",
        (session['user_id'],)
    ).fetchall()
    stats = {
        'total': len(incidents),
        'reported': sum(1 for i in incidents if i['status'] == 'Reported'),
        'investigating': sum(1 for i in incidents if i['status'] == 'Under Investigation'),
        'resolved': sum(1 for i in incidents if i['status'] == 'Resolved'),
    }
    db.close()
    return render_template('officer_dashboard.html', incidents=incidents, stats=stats)

@officer_bp.route('/report', methods=['GET', 'POST'])
@require_officer
def report_incident():
    error = None
    success = None

    if request.method == 'POST':
        inc_type = request.form.get('type', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        severity = request.form.get('severity', '').strip()

        if not all([inc_type, location, description, severity]):
            error = 'All fields are required.'
        elif severity not in ('Low', 'Medium', 'High'):
            error = 'Invalid severity value.'
        else:
            db = get_db()
            cursor = db.execute(
                "INSERT INTO incidents (type, location, description, severity, user_id) VALUES (?, ?, ?, ?, ?)",
                (inc_type, location, description, severity, session['user_id'])
            )
            incident_id = cursor.lastrowid

            # Handle image upload
            file = request.files.get('image')
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                analysis = analyze_image(filepath)
                db.execute(
                    "INSERT INTO images (file_path, analysis_result, incident_id) VALUES (?, ?, ?)",
                    (filename, analysis, incident_id)
                )

            db.commit()
            db.close()
            return redirect(url_for('officer.dashboard'))

    incident_types = [
        'Illegal Crossing', 'Smuggling', 'Armed Intrusion',
        'Vehicle Breach', 'Drone Activity', 'Suspicious Activity',
        'Document Fraud', 'Other'
    ]
    return render_template('report_incident.html', error=error, incident_types=incident_types)

@officer_bp.route('/incident/<int:incident_id>')
@require_officer
def incident_detail(incident_id):
    db = get_db()
    incident = db.execute(
        """SELECT i.*, u.full_name, u.username FROM incidents i 
           JOIN users u ON i.user_id = u.id WHERE i.id = ?""",
        (incident_id,)
    ).fetchone()

    if not incident:
        db.close()
        return "Incident not found", 404

    # Officers can only view their own incidents
    if session['role'] == 'officer' and incident['user_id'] != session['user_id']:
        db.close()
        return "Unauthorized", 403

    images = db.execute(
        "SELECT * FROM images WHERE incident_id = ?", (incident_id,)
    ).fetchall()
    db.close()
    return render_template('incident_detail.html', incident=incident, images=images)
