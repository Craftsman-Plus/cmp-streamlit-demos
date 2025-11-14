# Craftsman+ Streamlit Demos

This repository contains Streamlit demonstration applications for various Craftsman+ AI services.

## Available Apps

### 1. Playable Content Generator (`playable_app.py`)
Generate playable content with various templates and themes.

### 2. Brand Guidelines Validator (`validation_app.py`)
Validate playable images against brand guidelines using AI.

## Prerequisites

- Python 3.8+
- AWS credentials configured (for authentication)
- Access to Craftsman+ AI services

## Installation

1. Clone or navigate to this repository:
```bash
cd temp/cmp-streamlit-demos
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Apps

### Brand Guidelines Validator

```bash
streamlit run validation_app.py
```

Features:
- 📄 Upload brand guidelines as PDF
- 🖼️ Upload playable images for validation
- 🤖 Choose between Vision-based or Text-based validation
- ✅ Get detailed compliance results

### Playable Content Generator

```bash
streamlit run playable_app.py
```

Features:
- Generate playable content with various templates
- Create image variations
- Perform inpainting operations

## Authentication

All apps require authentication using:
- Email
- Password
- Client ID (pre-configured)

Default client ID: `4djrt5jve4ud0de66i75splf7l`

## API Endpoints

The apps connect to the following endpoints:
- **Base URL**: `https://ai.dev.craftsmanplus.com/api`
- **Image Validation**: `/images/validate`
- **Image Variation**: `/images/variation`
- **Image Edit**: `/images/edit`
- **Playable Generation**: `/playable/generate`
- **Jobs Status**: `/jobs/{job_id}`

## Validation App Usage

1. **Authenticate** on the Home page
2. Navigate to **Image Validation**
3. Enter a **brand name** (e.g., "slack", "coca-cola")
4. (Optional) Upload brand guidelines PDF
   - If not uploaded, the system will fetch from S3 using the brand name
5. Upload an **image** to validate
6. Choose validation mode:
   - **Vision-based**: Uses AI to directly analyze the image
   - **Text-based**: Requires uploaded guidelines, uses text analysis
7. Click **Validate Image**
8. Review results:
   - ✅ Compliant or ❌ Not Compliant
   - Detailed reasons if not compliant
   - Download results as JSON

## Validation Modes

### Vision-based (Recommended)
- Uses OpenAI's vision capabilities
- Analyzes image directly
- Faster and more accurate
- No need to upload guidelines

### Text-based
- Requires brand guidelines PDF
- Extracts text from PDF
- Compares image against text guidelines
- Useful when specific text analysis is needed

## Troubleshooting

### Authentication Issues
- Ensure your AWS credentials are configured
- Verify email and password are correct
- Check that the client ID is valid

### PDF Upload Issues
- Ensure the PDF is not password-protected
- Check that the PDF contains extractable text
- Try re-uploading the file

### Image Upload Issues
- Supported formats: PNG, JPG, JPEG
- Ensure image file is not corrupted
- Check file size (should be reasonable)

### API Errors
- Verify you have access to the AI service endpoints
- Check your network connection
- Ensure the service is running

## Development

### Adding New Features

To add new validation features:
1. Update `validation_app.py` with new UI components
2. Modify the validation payload in the `validate_image()` function
3. Update the results display section

### Testing

Test the validation endpoint directly:
```python
from authenticate import authenticate_and_get_token
import base64
import requests

# Authenticate
token = authenticate_and_get_token(email, password, client_id)

# Encode image
with open('image.jpg', 'rb') as f:
    image_b64 = base64.b64encode(f.read()).decode('utf-8')

# Validate
response = requests.post(
    'https://ai.dev.craftsmanplus.com/api/images/validate',
    json={
        'image': image_b64,
        'brand': 'slack',
        'vision': True
    },
    headers={'Authorization': token}
)

print(response.json())
```

## Contributing

When contributing:
1. Test authentication flow
2. Verify all API endpoints
3. Check error handling
4. Update documentation

## Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation
- Contact the Craftsman+ team

## License

Proprietary - Craftsman+

