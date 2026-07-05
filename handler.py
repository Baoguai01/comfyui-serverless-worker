import json
import base64
import time
import requests
import runpod

# =========================
# ComfyUI 地址（容器内）
# =========================
COMFYUI_URL = "http://127.0.0.1:8188"

# =========================
# workflow 路径
# =========================
WORKFLOW_DIR = "/workspace/runpod-slim/AI-Project/workflows"


# =========================
# 读取 workflow
# =========================
def load_workflow(filename):
    path = f"{WORKFLOW_DIR}/{filename}"
    with open(path, "r") as f:
        return json.load(f)


# =========================
# 上传图片到 ComfyUI
# =========================
def upload_image(image_base64, filename="input.png"):
    image_bytes = base64.b64decode(image_base64)

    files = {
        "image": (filename, image_bytes, "image/png")
    }

    resp = requests.post(
        f"{COMFYUI_URL}/upload/image",
        files=files
    )
    resp.raise_for_status()

    return resp.json()["name"]


# =========================
# 替换 workflow 中 LoadImage
# =========================
def patch_workflow(workflow, image_name):
    for node_id, node in workflow.items():
        if node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = image_name
    return workflow


# =========================
# 提交任务
# =========================
def queue_prompt(workflow):
    resp = requests.post(
        f"{COMFYUI_URL}/prompt",
        json={"prompt": workflow}
    )
    resp.raise_for_status()
    return resp.json()["prompt_id"]


# =========================
# 等待结果
# =========================
def wait_result(prompt_id, timeout=120):
    start = time.time()

    while time.time() - start < timeout:
        history = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
        if history.status_code == 200:
            data = history.json()
            if prompt_id in data and data[prompt_id]:
                outputs = data[prompt_id]["outputs"]

                images = []
                for node in outputs.values():
                    if "images" in node:
                        for img in node["images"]:
                            images.append(img["filename"])

                return images

        time.sleep(1)

    raise TimeoutError("ComfyUI timeout")


# =========================
# 主 handler（RunPod入口）
# =========================
def handler(event):
    input_data = event["input"]

    prompt = input_data.get("prompt", "")
    image_base64 = input_data.get("image", None)
    workflow_file = input_data.get("workflow", "flux-2img api.json")

    # 1. load workflow
    workflow = load_workflow(workflow_file)

    # 2. upload image（如果有）
    if image_base64:
        image_name = upload_image(image_base64)
        workflow = patch_workflow(workflow, image_name)

    # 3. 写入 prompt（CLIPTextEncode节点）
    for node_id, node in workflow.items():
        if node.get("class_type") == "CLIPTextEncode":
            node["inputs"]["text"] = prompt

    # 4. submit
    prompt_id = queue_prompt(workflow)

    # 5. wait result
    images = wait_result(prompt_id)

    # 6. return result
    return {
        "status": "success",
        "prompt_id": prompt_id,
        "images": images,
        "image_url": [
            f"{COMFYUI_URL}/view?filename={img}" for img in images
        ]
    }


# =========================
# RunPod 启动
# =========================
runpod.serverless.start({
    "handler": handler
})
