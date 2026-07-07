import runpod
import json
import base64
import uuid
import os
import requests
import time


COMFYUI_URL = "http://127.0.0.1:8188"


WORKFLOW_PATH = "/app/workflows/flux-2img-api.json"


def load_workflow():

    with open(WORKFLOW_PATH, "r") as f:
        return json.load(f)



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

    try:

        inp = event["input"]


        prompt = inp.get(
            "prompt",
            "a beautiful image"
        )


        image_base64 = inp.get(
            "image",
            None
        )


        workflow = load_workflow()



        # node 19
        workflow["19"]["inputs"]["text"] = prompt



        # node 63 LoadImage

        if image_base64:


            input_dir="/workspace/ComfyUI/input"

            os.makedirs(
                input_dir,
                exist_ok=True
            )


            filename="input.png"


            filepath=os.path.join(
                input_dir,
                filename
            )


            with open(filepath,"wb") as f:

                f.write(
                    base64.b64decode(image_base64)
                )


            workflow["63"]["inputs"]["image"] = filename



        result = queue_prompt(workflow)


        return {

            "status":"success",

            "prompt_id":result.get("prompt_id")

        }



    except Exception as e:


        return {

            "status":"error",

            "message":str(e)

        }



runpod.serverless.start({
    "handler":handler
})
