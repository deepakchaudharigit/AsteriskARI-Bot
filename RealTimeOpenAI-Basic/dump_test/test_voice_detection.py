#!/usr/bin/env python3
"""
Test voice detection sensitivity
"""

import pyaudio
import audioop
import time
import numpy as np
from colorama import init, Fore

init(autoreset=True)

def test_voice_detection():
    # Audio configuration
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    CHANNELS = 1
    
    audio = pyaudio.PyAudio()
    
    print(f"{Fore.YELLOW}🎤 Testing voice detection...")
    print(f"{Fore.CYAN}Speak into your microphone to test sensitivity")
    print(f"{Fore.CYAN}Press Ctrl+C to stop")
    
    # Calibrate
    print(f"{Fore.YELLOW}📊 Measuring ambient noise for 2 seconds...")
    
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    noise_samples = []
    for _ in range(int(2 * SAMPLE_RATE / CHUNK_SIZE)):
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        rms = audioop.rms(data, 2)
        noise_samples.append(rms)
    
    avg_noise = np.mean(noise_samples)
    max_noise = np.max(noise_samples)
    speech_threshold = max(avg_noise * 2.0, 300)
    
    print(f"{Fore.GREEN}✅ Calibration complete!")
    print(f"{Fore.CYAN}📈 Average noise: {avg_noise:.0f}")
    print(f"{Fore.CYAN}📈 Max noise: {max_noise:.0f}")
    print(f"{Fore.CYAN}📈 Speech threshold: {speech_threshold:.0f}")
    print()
    print(f"{Fore.YELLOW}🎤 Now monitoring... Speak to test!")
    
    try:
        while True:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            rms = audioop.rms(data, 2)
            
            if rms > speech_threshold:
                status = f"{Fore.GREEN}🔊 SPEECH DETECTED"
            elif rms > avg_noise * 1.5:
                status = f"{Fore.YELLOW}🔉 NOISE"
            else:
                status = f"{Fore.BLUE}🔇 SILENCE"
            
            print(f"\r{status} - RMS: {rms:4.0f} (Threshold: {speech_threshold:.0f})    ", end="", flush=True)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}👋 Test completed!")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    test_voice_detection()