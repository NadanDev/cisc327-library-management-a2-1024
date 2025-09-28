"""
Borrowing Routes - Book borrowing and returning endpoints
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from library_service import get_patron_status_report

status_bp = Blueprint('status', __name__)

@status_bp.route('/status', methods=['GET'])
def patron_status():
    """
    Process patron status report request.
    Web interface for R7: Patron Status Report
    """
    patron_id = request.args.get('patron_id', '').strip()
    
    status = get_patron_status_report(patron_id)

    return render_template('patron_status.html', patron_id=patron_id, status=status)