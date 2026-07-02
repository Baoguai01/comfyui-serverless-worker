FROM runpod/comfyui:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py .

RUN mkdir -p /workspace/ComfyUI/user/default/workflows

CMD ["python", "-u", "handler.py"]
