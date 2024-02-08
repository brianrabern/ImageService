from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import requests
from io import BytesIO
from PIL import Image


app = FastAPI()

def resize_with_aspect(image, width):
	aspect_ratio = width / image.width
	height = round(image.height * aspect_ratio)
	return image.resize((width, height))


@app.get("/resize/")
async def resize(image_url: str,size: str,format: str):
	try:
		response = requests.get(image_url)

		if response.status_code != 200:
			raise HTTPException(status_code=response.status_code, detail="Failed to fetch the image")

		image_data = BytesIO(response.content)
		original_image = Image.open(image_data)

		resized_image = resize_with_aspect(original_image, int(size))
		resized_image_data = BytesIO()
		resized_image.save(resized_image_data, format=format)
		resized_image_bytes = resized_image_data.getvalue()

		return Response(content=resized_image_bytes, media_type=f"image/{format}")

	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
