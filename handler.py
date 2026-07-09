import json
import base64
import time
import random
import requests
import runpod

# ComfyUI 内部 API 地址（容器内访问）
COMFYUI_URL = "http://127.0.0.1:8188"

# 工作流文件路径（挂载到 /workspace/ComfyUI/user/default/workflows/）
WORKFLOW_DIR = "/workspace/ComfyUI/user/default/workflows"

def load_workflow(filename):
    with open(f"{WORKFLOW_DIR}/{filename}", "r") as f:
        return json.load(f)

def run_comfyui(workflow, image_node_map, output_node_ids):
    """
    上传图片 -> 修改工作流 -> 提交 -> 轮询结果
    image_node_map: { "63": image_bytes, "64": image_bytes ... }
    """
    uploaded_files = {}
    
    # 1. 上传所有图片
    for node_id, img_bytes in image_node_map.items():
        files = {"image": (f"input_{node_id}.png", img_bytes)}
        resp = requests.post(f"{COMFYUI_URL}/upload/image", files=files)
        resp.raise_for_status()
        uploaded_files[node_id] = resp.json()["name"]
    
    # 2. 修改工作流中的 LoadImage 节点

