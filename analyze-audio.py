import librosa
import librosa.display
import matplotlib.pyplot as plt

y, sr = librosa.load("suzanne-kraft.mp3")
harmonic, percussive = librosa.effects.hpss(y)

# Plot
plt.figure(figsize=(10, 4))
librosa.display.waveshow(harmonic, sr=sr, alpha=0.5, label='Harmonic')
librosa.display.waveshow(percussive, sr=sr, color='r', alpha=0.5, label='Percussive')
plt.title('Harmonic vs Percussive Content')
plt.legend()
plt.tight_layout()
plt.show()