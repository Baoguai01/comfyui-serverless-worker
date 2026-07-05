import json
import base64
import os
import requests
import runpod

COMFY_URL = os.getenv("COMFY_URL", "http://127.0.0.1:8188/prompt")


# -----------------------------
# 1. base64 -> ComfyUI input image
# -----------------------------
def save_base64_image(base64_str, filename="input.png"):
    img_data = base64.b64decode(base64_str)
    path = f"/tmp/{filename}"
    with open(path, "wb") as f:
        f.write(img_data)
    return path


# -----------------------------
# 2. 替换 workflow 参数
# -----------------------------
def prepare_workflow(workflow, prompt, image_path=None):
    for node_id, node in workflow.items():

        # 文本 prompt
        if "inputs" in node and "text" in node["inputs"]:
            node["inputs"]["text"] = prompt

        # LoadImage 节点
        if node.get("class_type") == "LoadImage" and image_path:
            node["inputs"]["image"] = image_path

    return workflow


# -----------------------------
# 3. 调用 ComfyUI
# -----------------------------
def run_comfy(workflow):
    res = requests.post(COMFY_URL, json={"prompt": workflow})
    return res.json()


# -----------------------------
# 4. RunPod Serverless 入口
# -----------------------------
def handler(event):
    try:
        input_data = event.get("input", {})

        prompt = input_data.get("prompt", "")
        image_base64 = input_data.get("image")

        # workflow
        workflow_path = "/workspace/runpod-slim/AI-Project/workflows/flux-2img api.json"

        workflow = json.load(open(workflow_path, "r"))

        image_path = None
        if image_base64:
            image_path = save_base64_image(image_base64)

        workflow = prepare_workflow(workflow, prompt, image_path)

        result = run_comfy(workflow)

        return {
            "status": "success",
            "result": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


runpod.serverless.start({"handler": handler})
