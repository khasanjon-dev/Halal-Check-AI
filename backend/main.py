import os
import uuid

import magic
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Upload API Service",
    description="""
This API allows users to upload **images** and **text files** for analysis.

### Endpoints:
- **POST** `/analyze-image` → Upload and validate an image  
- **POST** `/analyze-text` → Upload a text input  
- **GET** `/` → Health check  
    """,
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories if they don't exist
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/texts", exist_ok=True)

# Allowed image MIME types
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]


class UploadResponse(BaseModel):
    status: str
    message: str
    filename: str


@app.post(
    "/analyze-image",
    response_model=UploadResponse,
    summary="Upload and analyze an image",
    description="""
Upload an image file (JPEG, PNG, GIF, WEBP).  
The file will be validated and saved on the server.

**Returns:**  
- Status message  
- Filename of the saved image  
""",
)
async def analyze_image(
    image: UploadFile = File(..., description="Image file to upload")
):
    try:
        # Check if neither image nor text is provided
        if not image:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Please provide either an image",
                },
            )

        # Handle image upload
        if image:
            # Validate file type
            file_content = await image.read()
            file_type = magic.from_buffer(file_content, mime=True)

            if file_type not in ALLOWED_IMAGE_TYPES:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
                    },
                )

            # Generate unique filename
            file_extension = (
                image.filename.split(".")[-1] if "." in image.filename else "jpg"
            )
            filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join("uploads/images", filename)

            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)

            return {
                "status": "success",
                "message": f"Image uploaded successfully: {filename}",
                "filename": filename,
            }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Internal server error: {str(e)}"},
        )


@app.post(
    "/analyze-text",
    response_model=UploadResponse,
    summary="Upload and analyze text",
    description="""
Submit a text input for analysis.  
The text will be saved as a `.txt` file on the server.

**Returns:**  
- Status message  
- Filename of the saved text  
""",
)
async def analyze_text(text: str = Form(..., description="Text content to upload")):
    try:

        if not text:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Please provide a text"},
            )
        if len(text.strip()) == 0:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Text cannot be empty"},
            )
        filename = f"{uuid.uuid4()}.txt"
        file_path = os.path.join("uploads/texts", filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        return {
            "status": "success",
            "message": f"Text Uploaded successfully: {filename}",
            "filename": filename,
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Internal server error: {str(e)}"},
        )


@app.get(
    "/",
    summary="API status check",
    description="Simple endpoint to verify that the Upload API is running.",
)
async def root():
    return {"message": "Upload API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
