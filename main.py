def main():
    import os
    os.environ["MODELSCOPE_CACHE"] = "./models"
    
    from funasr import AutoModel

    model_dir = "FunAudioLLM/Fun-ASR-Nano-2512"

    wav_path = "./data/1.mp3"
    model = AutoModel(
        model=model_dir,
        device="cuda:0",
        disable_update=True,
        trust_remote_code=True,
        remote_code="./funasr_custom_arch/model.py",
    )
    res = model.generate(input=[wav_path], cache={}, batch_size=1, language="中文", itn=True)
    text = res[0]["text"]
    print(text)


if __name__ == "__main__":
    main()
