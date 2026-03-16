from huggingface_hub import hf_hub_download

repo_id = "yandex/YandexGPT-5-Lite-8B-instruct-GGUF"
filename = "YandexGPT-5-Lite-8B-instruct-Q4_K_M.gguf"  # или другой нужный файл

model_path = hf_hub_download(
    repo_id=repo_id,
    filename=filename,
    local_dir="/Users/dariprim/Documents/models",          # сохранить в папку models
    local_dir_use_symlinks=False
)
print(f"Модель сохранена в: {model_path}")