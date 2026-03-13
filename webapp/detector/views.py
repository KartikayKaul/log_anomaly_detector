from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LogForm
from .models import LogEntry
from .utils import detect

import yaml
import random
from django.http import JsonResponse, HttpResponse, FileResponse




# ---------------- DASHBOARD ---------------- #

def dashboard(request):
    logs = LogEntry.objects.all().order_by('-created_at')

    total_logs = logs.count()
    anomaly_count = logs.filter(prediction='anomaly').count()
    normal_count = logs.filter(prediction='normal').count()

    anomaly_rate = 0
    if total_logs > 0:
        anomaly_rate = round((anomaly_count / total_logs) * 100, 2)

    context = {
        'total_logs': total_logs,
        'anomaly_count': anomaly_count,
        'normal_count': normal_count,
        'anomaly_rate': anomaly_rate,
        'recent_logs': logs[:5]
    }

    return render(request, 'dashboard.html', context)


# ---------------- TESTING PAGE ---------------- #

def testing(request):
    form = LogForm()
    result = None

    if request.method == "POST":
        action = request.POST.get("action")

        # -------- Single Log Detection -------- #
        if action == "single_detect":
            form = LogForm(request.POST)

            if form.is_valid():
                log_line = form.cleaned_data.get("log_line")

                if log_line:
                    prediction = detect(log_line)[0]

                    LogEntry.objects.create(
                        log_line=log_line,
                        prediction=prediction
                    )

                    result = prediction
                    messages.success(request, "Log processed successfully!")

        # -------- File Detection -------- #
        elif action == "file_detect":
            log_file = request.FILES.get("log_file")
            if log_file:
                try:
                    lines = log_file.read().decode("utf-8").splitlines()
                    lines = [l for l in lines if l.strip()]
                    
                    predictions = detect(lines)

                    entries = [
                        LogEntry(log_line=line, prediction=pred) for line, pred in zip(lines, predictions)
                    ]

                    LogEntry.objects.bulk_create(entries, batch_size=1000)

                    result = "File Processed Successfully"
                    messages.success(request, result)

                except Exception as e:
                    messages.error(request, f"Error: {e}")

    logs = LogEntry.objects.all().order_by('-created_at')

    return render(request, "testing.html", {
        "form": form,
        "logs": logs,
        "result": result
    })
# ---------------- CONFIG PAGE ---------------- #

def config_page(request):

    result_data = None

    if request.method == "POST":
        action = request.POST.get("action")

        # -------- Generate Config (LEFT FORM) -------- #
        if action == "add_config":

            start_time = request.POST.get("start_time")
            end_time = request.POST.get("end_time")
            total_logs = request.POST.get("total_logs")
            normal_weight = request.POST.get("normal_weight")
            user_count = request.POST.get("user_count")

            if start_time and end_time:
                result_data = f"""
Configuration Generated Successfully!

Start Time : {start_time}
End Time   : {end_time}
Total Logs : {total_logs}
Normal %   : {normal_weight}
Users      : {user_count}
                """

                messages.success(request, "Configuration generated successfully!")
            else:
                messages.error(request, "Start and End time required!")

        # -------- Upload Config File (RIGHT FORM) -------- #
        elif action == "upload_config_file":
            from pathlib import Path
            from core.data_pipeline import generate_data
            config_file = request.FILES.get("config_file")
            
            if config_file:
                try:
                    asset_dir = Path("../assets/temp")
                    asset_dir.mkdir(parents=True, exist_ok=True)

                    config_path = asset_dir / config_file.name
                    with open(config_path, "wb") as f:
                        for chunk in config_file.chunks():
                            f.write(chunk)

                    json_out = Path("../assets/data/log_data_train3.jsonl")
                    log_out = Path("../assets/logs/logs3.log")

                    generate_data(
                        str(config_path),
                        str(json_out),
                        str(log_out)
                    )

                    result_data = f"""
Logs Generated Successfully!

Config File : {config_file.name}
JSON Output : {json_out}
Log Output  : {log_out}
"""
                    messages.success(request, "Logs generated successfully!")
                except Exception:
                    messages.error(request, "Error reading file.")
            else:
                messages.error(request, "No file selected!")

    # -------- Show All Anomalies -------- #
    anomalies = LogEntry.objects.filter(
        prediction="anomaly"
    ).order_by('-created_at')

    return render(request, "config.html", {
        "anomalies": anomalies,
        "result_data": result_data   
    })



# ----------------Generate Logs Function----------------#

def generate_logs_from_config(config):

    users = config.get("users", [])
    endpoints = config.get("endpoints", [])
    ips = config.get("ips", [])
    total_logs = config.get("total_logs", 50)

    generated_logs = []

    for i in range(total_logs):

        user = random.choice(users)
        ip = random.choice(ips)
        endpoint = random.choice(endpoints)

        status = random.choice([200, 200, 200, 500, 404])
        response_time = random.randint(10, 2000)

        log_line = f"{user} | {ip} | {endpoint} | {status} | {response_time}ms"

        generated_logs.append(log_line)

        LogEntry.objects.create(
            log_line=log_line,
            prediction="normal"
        )

    return generated_logs



#-------------------Config Generate API (AJAX)--------------------#

def generate_logs(request):

    if request.method == "POST":

        config_data = yaml.safe_load(request.body)

        logs = generate_logs_from_config(config_data)

        return JsonResponse({
            "status": "success",
            "logs": logs
        })
    

from pathlib import Path
from django.http import FileResponse, HttpResponse


def download_generated_file(request, file_type):

    if file_type == "json":
        file_path = Path("../assets/data/log_data_train3.jsonl")

    elif file_type == "log":
        file_path = Path("../assets/logs/logs3.log")

    else:
        return HttpResponse("Invalid file type", status=400)

    if not file_path.exists():
        return HttpResponse("File not found", status=40e4)

    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=file_path.name
    )



#-------------------wipe logs--------------------#

def wipe_logs(request):
    if request.method == "POST":
        LogEntry.objects.all().delete()
        messages.success(request, "All logs deleted successfully!")
    return redirect("home")