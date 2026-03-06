from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import detect
from .models import LogEntry
import json


# Single Log Detection API
@csrf_exempt
def detect_log_api(request):

    if request.method == "POST":
        try:
            body = json.loads(request.body)
            log_line = body.get("log_line")

            if not log_line:
                return JsonResponse(
                    {"error": "log_line is required"},
                    status=400
                )

            prediction = detect(log_line)

          
            LogEntry.objects.create(       # Save in DB
                log_line=log_line,
                prediction=prediction
            )

            return JsonResponse({
                "log_line": log_line,
                "prediction": prediction
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Only POST method allowed"}, status=405)


# File Upload Detection API
@csrf_exempt
def detect_file_api(request):
    if request.method == "POST":
        log_file = request.FILES.get("log_file")

        if not log_file:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        content = log_file.read().decode("utf-8")

     
        logs = content.strip().split("\n")

        results = []

        for log in logs:
            log = log.strip()
            if not log:
                continue

            if "ERROR" in log or "failed" in log.lower():
                prediction = "anomaly"
            else:
                prediction = "normal"

            results.append({
                "log_line": log,
                "prediction": prediction
            })

        return JsonResponse({
            "total_logs": len(results),
            "results": results
        })

    return JsonResponse({"message": "Only POST method allowed"}, status=405)