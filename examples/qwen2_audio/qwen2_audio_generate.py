from io import BytesIO
from urllib.request import urlopen
import librosa
import mindspore as ms
from mindspore import Tensor
from transformers import AutoProcessor, Qwen2AudioConfig
from mindway.transformers import Qwen2AudioForConditionalGeneration
import numpy as np
if __name__ == '__main__':
    model_name = "Qwen/Qwen2-Audio-7B"
    model = Qwen2AudioForConditionalGeneration.from_pretrained(
        model_name,
        mindspore_dtype=ms.bfloat16,
        attn_implementation="eager",
        tie_word_embeddings=False,
    )
    processor = AutoProcessor.from_pretrained(model_name)

    prompt = "<|audio_bos|><|AUDIO|><|audio_eos|>Generate the caption in English:"
    # url = "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen2-Audio/audio/glass-breaking-151256.mp3"
    # audio, _ = librosa.load(BytesIO(urlopen(url).read()), sr=self.processor.feature_extractor.sampling_rate)
    audio_path = "/path/to/audio"
    audio, _ = librosa.load(audio_path, sr=processor.feature_extractor.sampling_rate)

    inputs = processor(text=prompt, audios=audio, return_tensors="np")

    for key,value in inputs.items():
        if isinstance(value, np.ndarray):
            inputs[key] = ms.Tensor(value)
        if isinstance(value, list):
            inputs[key] = ms.Tensor(value)
        if inputs[key].dtype == ms.int64:
            inputs[key] = inputs[key].to(ms.int32)
        if key == 'input_features':
            inputs[key] = ms.Tensor(value).to(ms.bfloat16)

    # Generate
    generate_ids = model.generate(**inputs, max_new_tokens=30, use_cache=False)
    print(generate_ids)
    answer = processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    print("response:",answer)
    # "Generate the caption in English: Glass is breaking."
