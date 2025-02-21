from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import tweepy
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
# Load environment variables
load_dotenv()

app = FastAPI()

# X API credentials
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Open the uploaded image
        image = Image.open(file.file)

        # Define sizes
        sizes = [(300, 250), (728, 90), (160, 600), (300, 600)]
        resized_images = [image.resize(size) for size in sizes]

        # Save resized images temporarily
        image_paths = [f"resized_{size[0]}x{size[1]}.jpg" for size in sizes]
        for img, path in zip(resized_images, image_paths):
            img.save(path)

        # Authenticate with X API
        auth = tweepy.OAuth1UserHandler(
            CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)

        # Upload images to X
        media_ids = [api.media_upload(path).media_id_string for path in image_paths]
        api.update_status(status="Resized images", media_ids=media_ids)

        # Clean up temporary files
        for path in image_paths:
            os.remove(path)

        return JSONResponse(content={"message": "Images posted successfully!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "Image Resizer and X Publisher"}