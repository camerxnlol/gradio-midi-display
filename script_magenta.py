import gradio as gr
import magenta.music as mm
import plotly.graph_objects as go
import tempfile
from magenta.music import midi_io

def display_piano_roll_magenta(file_path):
    sequence = midi_io.midi_file_to_sequence_proto(file_path)
    if not sequence.notes:
        return "No notes found in MIDI file."
    
    fig = go.Figure()
    
    colors = ["blue", "red", "green", "purple", "orange", "brown", "pink", "gray"]
    
    track_dict = {}
    for note in sequence.notes:
        instrument = note.instrument
        if instrument not in track_dict:
            track_dict[instrument] = []
        track_dict[instrument].append((note.start_time, note.end_time, note.pitch))
    
    for i, (instrument, notes) in enumerate(track_dict.items()):
        color = colors[i % len(colors)]
        for start, end, pitch in notes:
            fig.add_trace(go.Scatter(
                x=[start, end],
                y=[pitch, pitch],
                mode='lines',
                line=dict(width=8, color=color),
                hoverinfo='x+y',
                name=f"Instrument {instrument}"
            ))

    fig.update_layout(
        title="MIDI Piano Roll (Magenta)",
        xaxis_title="Time (seconds)",
        yaxis_title="MIDI Pitch",
        yaxis=dict(autorange='reversed'),
        xaxis=dict(rangeslider=dict(visible=True), type="linear"),
        height=600,
        dragmode="pan",
        showlegend=True
    )

    return fig

def play_midi_magenta(file_path):
    sequence = midi_io.midi_file_to_sequence_proto(file_path)
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    mm.sequence_proto_to_pretty_midi(sequence).fluidsynth().write(temp_wav.name)
    return temp_wav.name

demo_magenta = gr.Blocks()
with demo_magenta:
    gr.Markdown("# MIDI Piano Roll Viewer (Magenta)")
    with gr.Row():
        input_area = gr.File(type="filepath", label="Upload MIDI File", scale=1)
        display_area = gr.Plot(scale=5)
    play_button = gr.Audio(type="filepath", label="Playback")
    
    input_area.change(display_piano_roll_magenta, inputs=input_area, outputs=display_area)
    input_area.change(play_midi_magenta, inputs=input_area, outputs=play_button)

demo_magenta.launch()
