FROM runpod/comfyui:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py .

COPY ComfyUI/custom_nodes /workspace/ComfyUI/custom_nodes

COPY ComfyUI/user /workspace/ComfyUI/user

COPY ComfyUI/extra_model_paths.yaml /workspace/ComfyUI/extra_model_paths.yaml

RUN mkdir -p /workspace/ComfyUI/user/default/workflows

CMD ["python", "-u", "handler.py"]
