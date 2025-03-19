from flask import Blueprint, request, jsonify
from core.llm_processor import LLMProcessor
from pydantic import BaseModel, ValidationError
import logging
from config import config

logger = logging.getLogger(__name__)

bp = Blueprint('actions', __name__, url_prefix='/action')

llm_processor = LLMProcessor()

# Define a Pydantic model for the expected request body.
class ActionRequest(BaseModel):
    content: str

@bp.route('', methods=['GET'])
def hello():
    return jsonify({"soludo": "hello", "config": config.AKASH_API_BASE_URL}), 200

@bp.route('', methods=['POST'])
def process_action():
    """
    Endpoint to process the 'content' received in the request body using the LLM.
    It expects a JSON payload with a 'content' field.
    Returns a JSON response with the extracted action, amount, and wallet, or an error.
    """
    try:
        action_request = ActionRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    result = llm_processor.process_content(action_request.content)

    if result:
        return jsonify(result), 200
    else:
        return jsonify({"error": "No se pudo procesar la acción o extraer la información"}), 500