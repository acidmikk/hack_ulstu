from pathlib import Path

import torch
from diffusers import DiffusionPipeline
import json
from profanity_check import predict, predict_prob


def generate():
    with open("promts.json", "r") as fh:
        data = json.load(fh)
        promts = data['to_gen']

    with open("promts.json", 'w') as json_file:
        if len(promts) > 50:
            data['to_gen'] = promts[50:]
            promts = promts[:50]
        else:
            data['to_gen'] = []
            json.dump(data, json_file)

    pipe = DiffusionPipeline.from_pretrained("models/XpucT/Deliberate", local_files_only=True)
    if torch.cuda.is_available():
        pipe.to("cuda")

    # pipe.safety_checker = lambda images, clip_input: (images, False)
    output = Path("./output")
    output.mkdir(parents=True, exist_ok=True)
    for i in range(len(promts)):
        images = pipe(promts[i], negative_prompt='').images
        if predict_prob(promts[i]) < 0.6:
            images[0].save(output / f"{promts[i]}.png")
            with open("promts.json", 'w') as json_file:
                data['already_gen'].append(promts[i])
                json.dump(data, json_file)


if __name__ == '__main__':
    generate()
