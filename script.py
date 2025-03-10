import gradio as gr
import pretty_midi
import plotly.graph_objects as go
import tempfile
import numpy as np
import soundfile as sf

# Provide the correct path to a soundfont file
SOUNDFONT_PATH = "/Users/cameronholt/Downloads/FluidR3_GM.sf2"  # Replace with actual path

def parse_midi(file_path):
    midi_data = pretty_midi.PrettyMIDI(file_path)
    tracks = {}
    
    for instrument in midi_data.instruments:
        track_name = instrument.name if instrument.name else f"Track {len(tracks) + 1}"
        tracks[track_name] = []
        for note in instrument.notes:
            tracks[track_name].append((note.start, note.end, note.pitch))
    
    return tracks, midi_data

def display_piano_roll(file_path):
    tracks, _ = parse_midi(file_path)
    if not tracks:
        return "No notes found in MIDI file."
    
    fig = go.Figure()
    
    colors = ["blue", "red", "green", "purple", "orange", "brown", "pink", "gray"]
    
    for i, (track_name, notes) in enumerate(tracks.items()):
        color = colors[i % len(colors)]  # Cycle through colors
        for start, end, pitch in notes:
            fig.add_trace(go.Scatter(
                x=[start, end],
                y=[pitch, pitch],
                mode='lines',
                line=dict(width=8, color=color),
                hoverinfo='x+y',
                name=track_name
            ))
    
    fig.update_layout(
        title="MIDI Piano Roll",
        xaxis_title="Time (seconds)",
        yaxis_title="MIDI Pitch",
        yaxis=dict(autorange='reversed'),  # High pitches on top
        xaxis=dict(rangeslider=dict(visible=True), type="linear"),
        height=600,
        dragmode="pan",
        showlegend=True
    )
    
    return fig

def play_midi(file_path):
    _, midi_data = parse_midi(file_path)

    # Ensure the soundfont file exists
    if not SOUNDFONT_PATH:
        return "Error: Soundfont file not found."

    # Generate raw audio data using fluidsynth
    audio_data = midi_data.fluidsynth(sf2_path=SOUNDFONT_PATH)

    # Create a temporary WAV file
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    
    # Write the NumPy array to a WAV file with the correct sample rate
    sf.write(temp_wav.name, audio_data, samplerate=44100)

    return temp_wav.name

# Gradio Interface
demo = gr.Blocks()
with demo:
    gr.Markdown("# MIDI Piano Roll Viewer")
    with gr.Row():
        input_area = gr.File(type="filepath", label="Upload MIDI File", scale=1)
        display_area = gr.Plot(scale=5)
    play_button = gr.Audio(type="filepath", label="Playback")
    
    input_area.change(display_piano_roll, inputs=input_area, outputs=display_area)
    input_area.change(play_midi, inputs=input_area, outputs=play_button)

demo.launch()
