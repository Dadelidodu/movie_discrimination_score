import requests
import streamlit as st
import pdfplumber
import plotly.graph_objects as go
import numpy as np

def extract_names_with_progress(pdf_url):
    progress_bar = st.progress(0)
    progress_text_bar = st.empty()

    if not pdf_url:
        st.warning("Please provide a PDF URL.")
        return None

    response = requests.get(pdf_url)
    pdf_path = 'temp.pdf'
    with open(pdf_path, 'wb') as file:
        file.write(response.content)
    progress_bar.progress(10)
    progress_text_bar.text("PDF downloaded.")

    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        total_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text += page.extract_text()
            progress = 10 + int((i + 1) / total_pages * 80)
            progress_bar.progress(progress)
            progress_text_bar.text(f"Extracting text from page {i + 1}/{total_pages}...")

    progress_bar.progress(100)
    progress_text_bar.text("Text extraction completed!")
    st.success("Text extracted successfully.")

    return text

def calculate_inclusion_metrics(male_matches, female_matches):
    total_male_dialogue = sum(length for _, length in male_matches)
    total_female_dialogue = sum(length for _, length in female_matches)
    
    female_to_male_dialogue = (total_female_dialogue / total_male_dialogue * 100) if total_male_dialogue > 0 else 0
    female_to_male_matches = (len(female_matches) / len(male_matches) * 100) if len(male_matches) > 0 else 0
    women_inclusion_score = (female_to_male_dialogue + female_to_male_matches) / 2

    return female_to_male_dialogue, female_to_male_matches, women_inclusion_score

def plot_radar_chart_plotly(female_to_male_dialogue, female_to_male_matches, women_inclusion_score):
    labels = ['Female to Male Dialogue %', 'Female to Male Character Count %', 'Women Inclusion Score']
    stats = [female_to_male_dialogue, female_to_male_matches, women_inclusion_score]
    stats += stats[:1]  # To close the loop on the radar chart
    labels += [labels[0]]  # Repeat the first label for the loop

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=stats,
        theta=labels,
        fill='toself',
        name='Inclusion Metrics',
        line_color='blue'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=np.arange(0, 101, 10)
            ),
        ),
        showlegend=False
    )
    
    return fig

def plot_combined_radar_chart_plotly(stats_1, stats_2, labels):
    # Extend stats to close the radar chart loop
    stats_1 += stats_1[:1]
    stats_2 += stats_2[:1]
    labels += [labels[0]]  # Repeat the first label for closing loop

    # Create the radar chart
    fig = go.Figure()

    # Add the first movie stats
    fig.add_trace(go.Scatterpolar(
        r=stats_1,
        theta=labels,
        fill='toself',
        name='Movie 1',
        line_color='blue',
        visible=True  # Initially visible
    ))

    # Add the second movie stats
    fig.add_trace(go.Scatterpolar(
        r=stats_2,
        theta=labels,
        fill='toself',
        name='Movie 2',
        line_color='red',
        visible=True  # Initially visible
    ))

    # Update the layout for radar chart
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=np.arange(0, 101, 10)
            ),
        ),
        showlegend=True
    )

    return fig


