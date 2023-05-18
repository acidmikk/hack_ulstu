import shutil

from diffusers import StableDiffusionPipeline


def main():
    _, cache_folder = StableDiffusionPipeline.from_pretrained("XpucT/Deliberate",
                                                              return_cached_folder=True)
    shutil.copytree(cache_folder, "models/XpucT/Deliberate", dirs_exist_ok=True)


if __name__ == '__main__':
    main()
