from flask import Blueprint, render_template, request, redirect, url_for, session
from models.database import get_db
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def require_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session['role'] != 'admin':
            return redirect(url_for('officer.dashboard'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@require_admin
def dashboard():
    db = get_db()

    severity_filter = request.args.get('severity', '')
    status_filter = request.args.get('status', '')
    date_filter = request.args.get('date', '')

    query = """SELECT i.*, u.full_name, u.username,
               (SELECT COUNT(*) FROM images WHERE incident_id = i.id) as image_count
               FROM incidents i JOIN users u ON i.user_id = u.id WHERE 1=1"""
    params = []

    if severity_filter:
        query += " AND i.severity = ?"
        params.append(severity_filter)
    if status_filter:
        query += " AND i.status = ?"
        params.append(status_filter)
    if date_filter:
        query += " AND DATE(i.datetime) = ?"
        params.append(date_filter)

    query += " ORDER BY i.datetime DESC"
    incidents = db.execute(query, params).fetchall()

    all_incidents = db.execute("SELECT * FROM incidents").fetchall()
    stats = {
        'total': len(all_incidents),
        'reported': sum(1 for i in all_incidents if i['status'] == 'Reported'),
        'investigating': sum(1 for i in all_incidents if i['status'] == 'Under Investigation'),
        'resolved': sum(1 for i in all_incidents if i['status'] == 'Resolved'),
        'high': sum(1 for i in all_incidents if i['severity'] == 'High'),
        'medium': sum(1 for i in all_incidents if i['severity'] == 'Medium'),
        'low': sum(1 for i in all_incidents if i['severity'] == 'Low'),
    }
    db.close()
    return render_template('admin_dashboard.html', incidents=incidents, stats=stats,
                           severity_filter=severity_filter, status_filter=status_filter,
                           date_filter=date_filter)

@admin_bp.route('/incident/<int:incident_id>')
@require_admin
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
    images = db.execute("SELECT * FROM images WHERE incident_id = ?", (incident_id,)).fetchall()
    db.close()
    return render_template('incident_detail.html', incident=incident, images=images, is_admin=True)

@admin_bp.route('/incident/<int:incident_id>/update_status', methods=['POST'])
@require_admin
def update_status(incident_id):
    new_status = request.form.get('status')
    valid_statuses = ['Reported', 'Under Investigation', 'Resolved']
    if new_status not in valid_statuses:
        return "Invalid status", 400
    db = get_db()
    db.execute("UPDATE incidents SET status = ? WHERE id = ?", (new_status, incident_id))
    db.commit()
    db.close()
    return redirect(url_for('admin.incident_detail', incident_id=incident_id))

@admin_bp.route('/image/<filename>')
@require_admin
def serve_image(filename):
    from flask import send_from_directory, current_app
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
