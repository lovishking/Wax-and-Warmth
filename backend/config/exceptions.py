from rest_framework.views import exception_handler


def _messages(value):
    if isinstance(value, dict):
        parts = []
        for key, child in value.items():
            child_text = _messages(child)
            if child_text:
                parts.append(f'{key}: {child_text}' if key != 'detail' else child_text)
        return ' '.join(parts)
    if isinstance(value, (list, tuple)):
        return ' '.join(filter(None, (_messages(item) for item in value)))
    return str(value) if value else ''


def api_exception_handler(exc, context):
    """Return a stable error envelope while preserving field-level details."""
    response = exception_handler(exc, context)
    if response is None:
        return None

    original = response.data
    message = _messages(original) or 'The request could not be processed.'

    response.data = {
        'success': False,
        'error': {
            'code': getattr(exc, 'default_code', 'request_error').upper(),
            'message': message,
        },
        'details': original,
    }
    return response
