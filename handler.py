import runpod
import json
import base64
import uuid
import os
import requests


COMFYUI_URL="http://127.0.0.1:8188"

WORKFLOW_PATH="/app/workflows/flux-2img-api.json"


def load_workflow():

    with open(WORKFLOW_PATH,"r") as f:
        return json.load(f)



def save_image(base64_data):

    input_dir="/workspace/ComfyUI/input"

    os.makedirs(
        input_dir,
        exist_ok=True
    )


    filename="input.png"


    path=os.path.join(
        input_dir,
        filename
    )


    with open(path,"wb") as f:

        f.write(
            base64.b64decode(base64_data)
        )


    return filename



def queue_prompt(workflow):

    payload={

        "prompt":workflow,

        "client_id":str(uuid.uuid4())

    }


    r=requests.post(

        f"{COMFYUI_URL}/prompt",

        json=payload

    )


    return r.json()



def handler(job):


    try:


        inp=job["input"]


        prompt=inp.get(
            "prompt",
            "换装"
        )


        image=inp["image"]



        workflow=load_workflow()



        # node 19
        workflow["19"]["inputs"]["text"]=prompt



        # node 63
        filename=save_image(image)


        workflow["63"]["inputs"]["image"]=filename



        result=queue_prompt(workflow)



        return {

            "status":"success",

            "prompt_id":result["prompt_id"]

        }



    except Exception as e:


        return {

            "status":"error",

            "message":str(e)

        }



runpod.serverless.start({

    "handler":handler

})
