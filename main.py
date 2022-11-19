from core.api.clone import clone_voice

if __name__ == '__main__':
    res = clone_voice('out/01.wav', "out", [], "out/03.wav")
    print(res)
