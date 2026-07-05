import runpod
import json
import base64
import uuid
import os
import requests

COMFYUI_URL = "http://127.0.0.1:8188"

WORKFLOW_PATH = "/workspace/runpod-slim/AI-Project/workflows/flux-2img api.json"


def load_workflow():
    with open(WORKFLOW_PATH, "r") as f:
        return json.load(f)


def set_node(workflow, node_id, key, value):
    workflow[node_id]["inputs"][key] = value


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def queue_prompt(workflow):
    payload = {
        "prompt": workflow,
        "client_id": str(uuid.uuid4())
    }

    r = requests.post(
        f"{COMFYUI_URL}/prompt",
        json=payload,
        timeout=600
    )

    return r.json()


def handler(event):
    """
    RunPod Serverless entry
    """

    try:
        inp = event["input"]

        prompt = inp.get("prompt", "a beautiful image")
        image_base64 = inp.get("image", None)

        workflow = load_workflow()

        # =========================
        # 1. 设置文本 prompt
        # node 19 = CLIPTextEncode
        # =========================
        workflow["19"]["inputs"]["text"] = prompt

        # =========================
        # 2. 处理输入图片（LoadImage node 63）
        # =========================
        if image_base64:
            img_path = "/tmp/input.png"

            with open(img_path, "wb") as f:
                f.write(base64.b64decode(image_base64))

            workflow["63"]["inputs"]["image"] = img_path

        # =========================
        # 3. 提交 ComfyUI
        # =========================
        result = queue_prompt(workflow)

        return {
            "status": "success",
            "comfyui": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


runpod.serverless.start({
    "handler": handler
})
