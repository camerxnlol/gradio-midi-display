import gradio as gr
import muspy
import plotly.graph_objects as go
import tempfile

def display_piano_roll_muspy(file_path):
    music = muspy.read_midi(file_path)
    
    if not music.tracks:
        return "No notes found in MIDI file."
    
    fig = go.Figure()

    colors = ["blue", "red", "green", "purple", "orange", "brown", "pink", "gray"]
    
    for i, track in enumerate(music.tracks):
        color = colors[i % len(colors)]
        for note in track.notes:
            fig.add_trace(go.Scatter(
                x=[note.time, note.time + note.duration],
                y=[note.pitch, note.pitch],
                mode='lines',
                line=dict(width=8, color=color),
                hoverinfo='x+y',
                name=track.name or f"Track {i+1}"
            ))

    fig.update_layout(
        title="MIDI Piano Roll (muspy)",
        xaxis_title="Time (ticks)",
        yaxis_title="MIDI Pitch",
        yaxis=dict(autorange='reversed'),
        xaxis=dict(rangeslider=dict(visible=True), type="linear"),
        height=600,
        dragmode="pan",
        showlegend=True
    )

    return fig

def play_midi(file_path):
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    muspy.read_midi(file_path).synthesize().write(temp_wav.name)
    return temp_wav.name

demo_muspy = gr.Blocks()
with demo_muspy:
    gr.Markdown("# MIDI Piano Roll Viewer (muspy)")
    with gr.Row():
        input_area = gr.File(type="filepath", label="Upload MIDI File", scale=1)
        display_area = gr.Plot(scale=5)
    play_button = gr.Audio(type="filepath", label="Playback")
    
    input_area.change(display_piano_roll_muspy, inputs=input_area, outputs=display_area)
    input_area.change(play_midi, inputs=input_area, outputs=play_button)

demo_muspy.launch()
