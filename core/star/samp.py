from pydub import AudioSegment
from pydub.silence import split_on_silence
import os


def split(sound):
    dBFS = sound.dBFS
    chunks = split_on_silence(sound,
                              min_silence_len=100,
                              silence_thresh=dBFS - 16,
                              keep_silence=100
                              )
    return chunks


def combine(_src):
    audio = AudioSegment.empty()
    for i, filename in enumerate(os.listdir(_src)):
        if filename.endswith('.wav'):
            filename = os.path.join(_src, filename)
            audio += AudioSegment.from_wav(filename)
    return audio


def save_chunks(chunks, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    counter = 0

    target_length = 5 * 1000
    output_chunks = [chunks[0]]
    for chunk in chunks[1:]:
        if len(output_chunks[-1]) < target_length:
            output_chunks[-1] += chunk
        else:
            # if the last output chunk is longer than the target length,
            # we can start a new one
            output_chunks.append(chunk)

    for chunk in output_chunks:
        chunk = chunk.set_frame_rate(24000)
        chunk = chunk.set_channels(1)
        counter = counter + 1
        print(os.path.join(directory, str(counter) + '.wav'))
        chunk.export(os.path.join(directory, str(counter) + '.wav'), format="wav")


if __name__ == '__main__':
    chunks = split(combine("voice"))
    save_chunks(chunks, "new")
