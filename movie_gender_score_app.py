import streamlit as st
import pandas as pd
import plotly.subplots as sp
import spacy
import re
from collections import defaultdict
from utils.all_functions import extract_names_with_progress, calculate_inclusion_metrics, plot_radar_chart_plotly, plot_combined_radar_chart_plotly

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def normalize_name(name):
    # Remove suffixes like (CONT'D), *, (VOICE), and trailing punctuation
    normalized_name = re.sub(r'\s*\(.*?\)|[\(\*].*|\s*\(CONT\'D\)\s*|\(VOICE\)|[.?!,;]$', '', name).strip().upper()
    # Remove triple letters
    normalized_name = re.sub(r'(.)\1{2,}', r'\1', normalized_name)
    # Check if EXT. or INT. or any other disallowed strings are in the normalized name
    if any(prefix in normalized_name for prefix in ['EXT.', 'INT.', 'EXT', 'INT','THE']):
        return None
    # Check if the name starts with EXT. or INT.
    if normalized_name.endswith(':'):
        return None
    # Use spaCy to check if the normalized name contains verbs
    doc = nlp(normalized_name)
    # Return None if the normalized name contains verbs
    if any(token.pos_ == ('VERB') for token in doc):
        return None
    return normalized_name

def update_dialogue_lengths(lines):
    dialogue_lengths = defaultdict(int)
    current_character = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Identify character names (assumed to be uppercase)
        if line.isupper():
            current_character = normalize_name(line)
        # Add dialogue length to the current character's entry
        elif current_character:
            dialogue_lengths[current_character] += len(line)

    return dialogue_lengths

def calculate_top_character_names(lines):
    dialogue_lengths = update_dialogue_lengths(lines)
    
    # Sort characters by their total dialogue length
    top_characters = sorted(dialogue_lengths.items(), key=lambda x: x[1], reverse=True)

    # Filter out entries with numbers in their names (if needed)
    top_characters = [(name, length) for name, length in top_characters if not re.search(r'\d', name)][:50]

    return top_characters

def compare_with_predefined_lists(top_characters, male_characters, female_characters):
    male_matches = []
    female_matches = []
    
    # Normalize predefined character names
    male_characters_normalized = [normalize_name(name) for name in male_characters]
    female_characters_normalized = [normalize_name(name) for name in female_characters]

    for name, length in top_characters:
        clean_name = normalize_name(name)
        if clean_name in male_characters_normalized:
            male_matches.append((clean_name, length))
        elif clean_name in female_characters_normalized:
            female_matches.append((clean_name, length))

    return male_matches, female_matches


# -------------------------------

# Streamlit app

st.title("The Movie Gender Score App")

# Option selection

option = st.selectbox(
    "Choose an option to get started:",
    ["Upload PDF URL", "Select from List", "Compare Movies"]
)

# Load PDF URLs from a local CSV file

csv_path = 'utils/csv_all_scripts.csv'  # Replace with your actual file path
pdf_data = pd.read_csv(csv_path)

if option == "Upload PDF URL":
    pdf_url = st.text_input("Enter the PDF URL:")
    if pdf_url:
        
            
                if 'extracted_text' not in st.session_state or st.session_state.pdf_url != pdf_url:
                    
            
                        st.write("Analyzing the PDF...")
                        st.session_state.extracted_text = extract_names_with_progress(pdf_url)
                        st.session_state.pdf_url = pdf_url  # Store the selected PDF URL

                        if st.session_state.extracted_text:
                            text = st.session_state.extracted_text
                            lines = text.split('\n')
                            st.session_state.top_characters = calculate_top_character_names(lines)

                # Use the stored top characters

                if 'top_characters' in st.session_state:

                        top_characters = st.session_state.top_characters

                        st.write("Select male and female characters from the PDF:")
                        character_names = [name for name, _ in top_characters]
                        male_characters = st.multiselect("Select male characters from PDF ", character_names)
                        female_characters = st.multiselect("Select female characters from PDF ", character_names)

                        submit = st.button("Submit")


                        if male_characters and female_characters:
                            
                            if submit:
                                
                                progress_bar = st.progress(0)
                                progress_bar.progress(50)
                                progress_text_bar = st.empty()
                                progress_text_bar.text("Processing analysis...")
                                
                                
                                male_matches, female_matches = compare_with_predefined_lists(top_characters, male_characters, female_characters)
                                
                                progress_bar.progress(100)
                                progress_text_bar.text("Analysis completed.")

                                female_to_male_dialogue, female_to_male_matches, women_inclusion_score = calculate_inclusion_metrics(male_matches, female_matches)


                                # Display results for both PDFs
                                st.write("### Results for PDF 1")
                                st.write(f"Percentage of Female to Male dialogue: {female_to_male_dialogue:.2f}%")
                                st.write(f"Percentage of Female to Male Characters: {female_to_male_matches:.2f}%")
                                st.write(f"Women Inclusion Score: {women_inclusion_score:.2f}%")

                                # Generate and display the radar chart for both PDFs
                                radar_chart_plotly = plot_radar_chart_plotly(female_to_male_dialogue, female_to_male_matches, women_inclusion_score)
                                

                                st.plotly_chart(radar_chart_plotly, use_container_width=True)

                        else:
                            st.warning("Please select male and female characters from both PDFs to proceed.")

elif option == "Select from List":
    
    # Create a dictionary where 'TITLE' is the display value and 'PDF_URL' is the return value
    
    pdf_choices = dict(zip(pdf_data['TITLE'], pdf_data['PDF_URL']))

# Use the titles for display, but return the corresponding PDF_URL
    
    selected_title = st.selectbox("Choose the movie from the list:", options=list(pdf_choices.keys()))

# Get the corresponding PDF_URL for the selected title
    
    pdf_url_selected = pdf_choices[selected_title]  # This will fetch the URL based on the title


    if pdf_url_selected:
        
            if 'extracted_text' not in st.session_state or st.session_state.pdf_url != pdf_url_selected:
                 
                 if st.button('Validate'):
                    st.write("Analyzing the PDF...")
                    st.session_state.extracted_text = extract_names_with_progress(pdf_url_selected)
                    st.session_state.pdf_url = pdf_url_selected  # Store the selected PDF URL

                    if st.session_state.extracted_text:
                        text = st.session_state.extracted_text
                        lines = text.split('\n')
                        st.session_state.top_characters = calculate_top_character_names(lines)

            # Use the stored top characters

            if 'top_characters' in st.session_state:

                    top_characters = st.session_state.top_characters

                    st.write("Select male and female characters from the PDF:")
                    character_names = [name for name, _ in top_characters]
                    male_characters = st.multiselect("Select male characters from PDF ", character_names)
                    female_characters = st.multiselect("Select female characters from PDF ", character_names)

                    submit = st.button("Submit")


                    if male_characters and female_characters:
                        
                        if submit:
                            
                            progress_bar = st.progress(0)
                            progress_bar.progress(50)
                            progress_text_bar = st.empty()
                            progress_text_bar.text("Processing analysis...")
                            
                            
                            male_matches, female_matches = compare_with_predefined_lists(top_characters, male_characters, female_characters)
                            
                            progress_bar.progress(100)
                            progress_text_bar.text("Analysis completed.")

                            female_to_male_dialogue, female_to_male_matches, women_inclusion_score = calculate_inclusion_metrics(male_matches, female_matches)


                            # Display results for both PDFs
                            st.write("### Results for PDF 1")
                            st.write(f"Percentage of Female to Male dialogue: {female_to_male_dialogue:.2f}%")
                            st.write(f"Percentage of Female to Male Characters: {female_to_male_matches:.2f}%")
                            st.write(f"Women Inclusion Score: {women_inclusion_score:.2f}%")

                            # Generate and display the radar chart for both PDFs
                            radar_chart_plotly = plot_radar_chart_plotly(female_to_male_dialogue, female_to_male_matches, women_inclusion_score)
                            

                            st.plotly_chart(radar_chart_plotly, use_container_width=True)

                    else:
                        st.warning("Please select male and female characters from PDF to proceed.")
            
# TO RUN APP LOCALLY = streamlit run 'movie_gender_score_app.py' in Terminal