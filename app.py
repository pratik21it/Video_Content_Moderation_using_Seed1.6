import streamlit as st
import os
import cv2
import base64
import requests
import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pathlib import Path
import time

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Set page configuration
st.set_page_config(page_title="Video Content Moderation", layout="wide")

# Define keyword categories for different types of content moderation
CONTENT_MODERATION_CATEGORIES = {
    "Violence Detection": [
        "violence", "violent", "fight", "fighting", "weapon", "gun", "knife", 
        "blood", "injury", "injured", "attack", "attacking", "hit", "hitting", 
        "punch", "punching", "kick", "kicking", "harm", "harming", "assault", 
        "assaulting", "battle", "war", "conflict", "abuse", "abusing", "threat", 
        "threatening", "danger", "dangerous", "hurt", "hurting", "wound", "wounding"
    ],
    "Sexual Content/Nudity": [
        "nude", "nudity", "naked", "sexual", "sex", "explicit", "pornography", "pornographic",
        "adult content", "erotic", "obscene", "intimate", "revealing", "inappropriate",
        "suggestive", "lewd", "indecent", "provocative", "sensual", "seductive"
    ],
    "Terrorism and Extremist Content": [
        "terrorism", "terrorist", "extremist", "extremism", "radical", "radicalization",
        "bomb", "bombing", "explosive", "attack", "jihad", "militant", "hostage",
        "propaganda", "recruitment", "indoctrination", "manifesto", "hate speech",
        "supremacist", "insurgent", "insurgency", "militia", "violent ideology"
    ],
    "Child Safety and Exploitation": [
        "child abuse", "child exploitation", "minor", "underage", "child endangerment",
        "child safety", "child harm", "child protection", "child victim", "child predator",
        "grooming", "trafficking", "exploitation", "vulnerable", "youth", "adolescent",
        "infant", "toddler", "baby", "school", "playground", "classroom"
    ],
    "Graphic or Disturbing Content": [
        "graphic", "disturbing", "gore", "gory", "gruesome", "brutal", "horrific",
        "shocking", "distressing", "traumatic", "upsetting", "offensive", "unsettling",
        "violent scene", "blood", "injury", "accident", "disaster", "death", "corpse",
        "mutilation", "torture", "suffering", "medical procedure", "surgery"
    ]
}

# For backward compatibility
DEFAULT_VIOLENCE_KEYWORDS = CONTENT_MODERATION_CATEGORIES["Violence Detection"]

# BytePlus API configuration
API_URL = "https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions"
# Store only the token without the Bearer prefix
API_KEY = "81a5d6cf-9e8d-41d3-b318-e67794fc4150"  # Just the token without Bearer

# Function to create folder for extracted frames
def create_folder(video_name):
    folder_name = os.path.splitext(video_name)[0]
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

# Function to extract frames from video
def extract_frames(video_file, folder_path, frame_interval=10):  # Changed from 5 to 10
    # Save uploaded video to a temporary file
    temp_video_path = os.path.join(folder_path, "temp_video.mp4")
    with open(temp_video_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    # Open the video file
    cap = cv2.VideoCapture(temp_video_path)
    frame_count = 0
    saved_frames = []
    
    # Read until video is completed
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break
        
        # Save every nth frame
        if frame_count % frame_interval == 0:
            frame_path = os.path.join(folder_path, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_path, frame)
            saved_frames.append(frame_path)
        
        frame_count += 1
    
    # Release the video capture object
    cap.release()
    
    # Remove temporary video file
    os.remove(temp_video_path)
    
    return saved_frames

# Function to encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to call BytePlus API for image captioning
def get_image_caption(image_path, api_key):
    base64_image = encode_image(image_path)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "seed-1-6-250615",
        "messages": [
            {
                "content": [
                    {
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                        "type": "image_url"
                    },
                    {
                        "text": "Describe what is happening in this image in detail. Focus on any actions, objects, and the overall scene. Please respond in English only.",
                        "type": "text"
                    }
                ],
                "role": "user"
            }
        ],
        "response_format": {"type": "text"},
        "system_prompt": "You are a helpful assistant that responds only in English."
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            if 'error' in response_data:
                return f"Error: {response_data['error']['message']}"
            return "Failed to get caption from API"
    except Exception as e:
        return f"API request error: {str(e)}"

# Function to extract keywords from caption
def extract_keywords(caption, stop_words=None):
    if stop_words is None:
        stop_words = set(stopwords.words('english'))
    
    # Tokenize the caption
    word_tokens = word_tokenize(caption.lower())
    
    # Remove stopwords and non-alphabetic tokens
    keywords = [word for word in word_tokens if word.isalpha() and word not in stop_words]
    
    # Get frequency distribution
    freq_dist = nltk.FreqDist(keywords)
    
    # Return the most common keywords (adjust the number as needed)
    return [word for word, freq in freq_dist.most_common(10)]

# Function to check if keywords contain violence-related terms
def check_violence(keywords, violence_keywords):
    violence_keywords_lower = [keyword.lower() for keyword in violence_keywords]
    return any(keyword.lower() in violence_keywords_lower for keyword in keywords)

# Main Streamlit app
def main():
    st.title("Video Content Moderation App")
    
    # API Key input
    api_key = st.text_input("BytePlus API Key", value=API_KEY, type="password")
    if not api_key:
        st.warning("Please enter your BytePlus API Key to use this application.")
        return
    
    # File uploader for video
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
    
    # Content moderation options
    st.subheader("Content Moderation Options")
    
    # Select moderation category
    moderation_category = st.selectbox(
        "Select content moderation type:",
        options=list(CONTENT_MODERATION_CATEGORIES.keys()),
        index=0
    )
    
    # Display selected category keywords
    selected_keywords = CONTENT_MODERATION_CATEGORIES[moderation_category]
    st.info(f"Selected category: **{moderation_category}**")
    
    # Custom keywords option
    use_default_keywords = st.checkbox("Use predefined keywords for selected category", value=True)
    
    if use_default_keywords:
        moderation_keywords = selected_keywords
        with st.expander("View predefined keywords"):
            st.write(", ".join(moderation_keywords))
    else:
        custom_keywords = st.text_area("Enter custom keywords for moderation (comma-separated)", 
                                    value=", ".join(selected_keywords))
        moderation_keywords = [keyword.strip() for keyword in custom_keywords.split(",") if keyword.strip()]
    
    if uploaded_file is not None:
        # Process button
        if st.button("Process Video"):
            with st.spinner("Processing video..."):
                # Create folder for frames
                folder_path = create_folder(uploaded_file.name)
                st.info(f"Created folder: {folder_path}")
                
                # Extract frames
                progress_bar = st.progress(0)
                st.info("Extracting frames...")
                frames = extract_frames(uploaded_file, folder_path, frame_interval=10)  # Using 10 as per previous modification
                st.success(f"Extracted {len(frames)} frames")
                
                # Process each frame
                st.subheader("Frame Analysis")
                col1, col2 = st.columns(2)
                
                all_keywords = []
                frame_results = []
                
                for i, frame_path in enumerate(frames):
                    progress_value = (i + 1) / len(frames)
                    progress_bar.progress(progress_value)
                    
                    with col1:
                        st.image(frame_path, caption=f"Frame {i+1}", width=300)
                    
                    with col2:
                        st.text(f"Processing frame {i+1}...")
                        caption = get_image_caption(frame_path, api_key)
                        st.text_area(f"Caption {i+1}", caption, height=150)
                        
                        # Extract keywords
                        keywords = extract_keywords(caption)
                        all_keywords.extend(keywords)
                        
                        # Check for moderation keywords
                        is_flagged = check_violence(keywords, moderation_keywords)  # Reusing the function
                        
                        # Display keywords with color coding
                        keyword_html = ""
                        for keyword in keywords:
                            color = "red" if keyword.lower() in [mk.lower() for mk in moderation_keywords] else "green"
                            keyword_html += f"<span style='color:{color}; font-weight:bold;'>{keyword}</span> "
                        
                        st.markdown(f"**Keywords:** {keyword_html}", unsafe_allow_html=True)
                        
                        frame_results.append({
                            "frame": i+1,
                            "path": frame_path,
                            "caption": caption,
                            "keywords": keywords,
                            "is_flagged": is_flagged
                        })
                        
                        # Add a separator between frames
                        st.markdown("---")
                
                # Overall results - Enhanced Summary Section
                st.header(f"📊 {moderation_category} Moderation Summary", divider="rainbow")
                
                # Get unique keywords and their frequencies
                all_keywords_freq = nltk.FreqDist(all_keywords)
                most_common_keywords = all_keywords_freq.most_common(20)
                
                # Create two columns for the summary
                summary_col1, summary_col2 = st.columns(2)
                
                with summary_col1:
                    # Display overall keywords with color coding
                    st.markdown("### Key Content Descriptors:")  
                    keyword_html = "<div style='background-color:#f0f2f6; padding:10px; border-radius:5px;'>"                  
                    for keyword, freq in most_common_keywords:
                        color = "red" if keyword.lower() in [mk.lower() for mk in moderation_keywords] else "green"
                        keyword_html += f"<span style='color:{color}; font-weight:bold; margin:3px; font-size:16px;'>{keyword} ({freq})</span> "                    
                    keyword_html += "</div>"
                    st.markdown(keyword_html, unsafe_allow_html=True)
                
                with summary_col2:
                    # Check if any frame contains flagged content
                    flagged_frames = [result for result in frame_results if result["is_flagged"]]
                    
                    # Calculate statistics
                    total_frames = len(frames)
                    flagged_frame_count = len(flagged_frames)
                    safe_percentage = ((total_frames - flagged_frame_count) / total_frames) * 100
                    
                    # Display statistics
                    st.markdown("### Content Safety Analysis:")
                    st.metric("Total Frames Analyzed", total_frames)
                    st.metric("Safe Content Percentage", f"{safe_percentage:.1f}%")
                    
                    if flagged_frames:
                        st.error(f"⚠️ Potentially harmful {moderation_category.lower()} detected in {flagged_frame_count} frames!")
                    else:
                        st.success(f"✅ No {moderation_category.lower()} detected in the video.")
                
                # Display detailed breakdown of potentially harmful frames if any
                if flagged_frames:
                    st.markdown(f"### 🚨 Potentially Harmful {moderation_category} Details:")                    
                    for ff in flagged_frames:
                        with st.expander(f"Frame {ff['frame']} Details"):
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.image(ff['path'], width=200)
                            with col2:
                                st.markdown("**Detected Keywords:**")
                                keyword_html = ""
                                for keyword in ff['keywords']:
                                    color = "red" if keyword.lower() in [mk.lower() for mk in moderation_keywords] else "green"
                                    keyword_html += f"<span style='color:{color}; font-weight:bold;'>{keyword}</span> "
                                st.markdown(keyword_html, unsafe_allow_html=True)
                                st.markdown(f"**Caption:** {ff['caption']}")

if __name__ == "__main__":
    main()