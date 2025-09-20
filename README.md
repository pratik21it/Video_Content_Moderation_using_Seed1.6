# Video Content Moderation App

A Streamlit application that uses BytePlus API for video content moderation. The app analyzes video frames for various types of content including violence, sexual content, terrorism, child safety concerns, and graphic/disturbing content.

## Features

- Upload and process video files
- Extract frames at specified intervals
- Analyze frames using BytePlus API for image captioning
- Detect potentially harmful content based on predefined or custom keywords
- Provide detailed analysis with visual indicators

## Requirements

- Python 3.6+
- Streamlit
- OpenCV
- NLTK
- Requests
- BytePlus API key

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`

## Usage

1. Enter your BytePlus API key
2. Upload a video file
3. Select content moderation type
4. Use predefined keywords or enter custom ones
5. Click "Process Video" to analyze

## Deployment

### Local Deployment
For local deployment, simply run:
```
streamlit run app.py
```

### AWS Deployment
To deploy this application on AWS EC2 Free Tier:

1. Follow the instructions in `AWS_DEPLOYMENT_GUIDE.md`
2. Alternatively, use the provided deployment script on your EC2 instance:
   ```
   ./deploy_to_ec2.sh
   ```

For detailed deployment instructions on Byteplus ECS Ubuntu 22.04, see the deployment guide.

## License

[Your chosen license]

## Author

[Your name/organization]
