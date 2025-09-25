#!/usr/bin/env python3
"""
Real-time speech detection test
"""

import pyaudio
import audioop
import time
import numpy as np
from colorama import init, Fore

init(autoreset=True)

def test_realtime_detection():
    # Audio configuration
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 512
    CHANNELS = 1
    
    audio = pyaudio.PyAudio()
    
    print(f"{Fore.YELLOW}🎤 Real-time speech detection test...")
    
    # Quick calibration
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    noise_samples = []
    for _ in range(int(1.5 * SAMPLE_RATE / CHUNK_SIZE)):
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        rms = audioop.rms(data, 2)
        noise_samples.append(rms)
    
    avg_noise = np.mean(noise_samples)
    max_noise = np.max(noise_samples)
    std_noise = np.std(noise_samples)
    
    speech_threshold = min(avg_noise * 1.8, max_noise * 1.3, avg_noise + 3 * std_noise, 400)
    
    print(f"{Fore.GREEN}📈 Threshold: {speech_threshold:.0f}")
    print(f"{Fore.CYAN}🎤 Speak to test detection...")
    
    speech_frames = []
    silence_frames = 0
    speech_detected = False
    
    try:
        while True:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            rms = audioop.rms(data, 2)
            
            has_voice = rms > speech_threshold
            
            if has_voice:
                if not speech_detected:
                    print(f"\n{Fore.GREEN}🎤 SPEECH START (RMS: {rms:.0f})")
                speech_frames.append(data)
                silence_frames = 0
                speech_detected = True
            else:
                silence_frames += 1
                
                if speech_detected and silence_frames > int(0.4 * SAMPLE_RATE / CHUNK_SIZE):
                    if len(speech_frames) > int(0.15 * SAMPLE_RATE / CHUNK_SIZE):
                        print(f"\n{Fore.BLUE}✅ SPEECH END - Would process {len(speech_frames)} frames")
                    else:
                        print(f"\n{Fore.YELLOW}⚠️ Speech too short - {len(speech_frames)} frames")
                    
                    speech_frames = []
                    speech_detected = False
                    silence_frames = 0
            
            # Show current status
            status = f"{Fore.GREEN}🔊" if has_voice else f"{Fore.BLUE}🔇"
            print(f"\r{status} RMS: {rms:4.0f} | Threshold: {speech_threshold:.0f}    ", end="", flush=True)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}👋 Test completed!")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    test_realtime_detection()