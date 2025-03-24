from flask import Blueprint

bp = Blueprint('status', __name__, url_prefix='/status')

@bp.route('', methods=['GET'])
def status():
    return "We are up!"