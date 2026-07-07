import runpod
import json
import base64
import uuid
import os
import requests
import subprocess
import time
import threading


# ==========================
# 路径配置
# ==========================

COMFYUI_PATH = "/workspace/runpod-slim/ComfyUI"

COMFYUI_URL = "http://127.0.0.1:8188"


WORKFLOW_PATH = "/app/workflows/flux-2img-api.json"


INPUT_PATH = "/workspace/runpod-slim/ComfyUI/input"



# ==========================
# 启动 ComfyUI
# ==========================

def start_comfyui():


    print("Starting ComfyUI...")


    cmd = [

        "python",

        f"{COMFYUI_PATH}/main.py",

        "--listen",

        "127.0.0.1",

        "--port",

        "8188"

    ]


    subprocess.Popen(

        cmd,

        cwd=COMFYUI_PATH

    )



    for i in range(120):

        try:

            r=requests.get(

                COMFYUI_URL,

                timeout=3

            )


            if r.status_code == 200:

                print("ComfyUI Ready")

                return True


        except Exception:

            pass


        time.sleep(2)



    raise Exception(
        "ComfyUI start timeout"
    )





# ==========================
# 加载workflow
# ==========================

def load_workflow():

    with open(
        WORKFLOW_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)





# ==========================
# 保存base64图片
# ==========================

def save_image(base64_data):


    os.makedirs(

        INPUT_PATH,

        exist_ok=True

    )


    filename="input.png"


    filepath=os.path.join(

        INPUT_PATH,

        filename

    )


    with open(filepath,"wb") as f:

        f.write(

            base64.b64decode(base64_data)

        )


    return filename





# ==========================
# 提交ComfyUI
# ==========================

def queue_prompt(workflow):


    payload={

        "prompt":workflow,

        "client_id":str(uuid.uuid4())

    }



    r=requests.post(

        f"{COMFYUI_URL}/prompt",

        json=payload,

        timeout=600

    )


    return r.json()





# ==========================
# RunPod handler
# ==========================

def handler(job):


    try:


        inp = job["input"]


        prompt = inp.get(

            "prompt",

            "change clothes"

        )


        image = inp.get(

            "image"

        )


        if not image:

            raise Exception(
                "image required"
            )



        workflow = load_workflow()



        # ==================
        # Node 19
        # Prompt
        # ==================

        workflow["19"]["inputs"]["text"] = prompt




        # ==================
        # Node 63
        # 用户图片
        # ==================

        filename = save_image(image)


        workflow["63"]["inputs"]["image"] = filename




        # ==================
        # Node64
        # 固定衣服图片
        #
        # workflow里面保持:
        #
        # clothes.jpg
        #
        # ==================



        result = queue_prompt(

            workflow

        )



        return {


            "status":"success",


            "result":result


        }




    except Exception as e:


        return {


            "status":"error",


            "message":str(e)


        }




# ==========================
# 启动Serverless
# ==========================

start_comfyui()


runpod.serverless.start({

    "handler":handler

})
