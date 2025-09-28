# rag_app/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .rag_engine import ask_question, FileNotFoundError, ValueError

@csrf_exempt
@require_http_methods(["POST"])
def rag_query(request):
    try:
        data = json.loads(request.body)
        question = data.get("question", "").strip()
        if not question:
            return JsonResponse({"error": "Вопрос не может быть пустым"}, status=400)

        answer = ask_question(question)
        return JsonResponse({"answer": answer})

    except FileNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=500)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Ошибка обработки: {str(e)}"}, status=500)