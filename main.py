from fastapi import FastAPI
from PIL import Image
from io import BytesIO
import requests
from fastapi.responses import Response
import base64

app = FastAPI()

DEFAULT_WIDTHS = [100, 200, 300]

def resize_with_aspect(image, width):
	aspect_ratio = width / image.width
	height = round(image.height * aspect_ratio)
	return image.resize((width, height))

@app.post("/thumbnail/")
async def create_thumbnail(image_url: str):
	try:
		response = requests.get(image_url)
		image_data = BytesIO(response.content)
		image = Image.open(image_data)

		size = 100,100
		image.thumbnail(size)
		output_buffer = BytesIO()
		image.save(output_buffer, format=image.format)
		thumbnail_image_data = output_buffer.getvalue()

		return Response(content=thumbnail_image_data, media_type="image/*")
	except Exception as e:
		print("Error:", e)
		return None

@app.post("/custom_resize/")
async def resize_image(image_url: str, size: int):
	try:
		response = requests.get(image_url)
		image_data = BytesIO(response.content)
		image = Image.open(image_data)

		original_width, original_height = image.size

		aspect_ratio = original_width / original_height

		resized_image = resize_with_aspect(image, size)
		resized_image_data = BytesIO()
		resized_image.save(resized_image_data, format="WEBP")
		image_format= Image.open(resized_image_data).format
		resized_image_bytes = resized_image_data.getvalue()
		encoded_data = base64.b64encode(resized_image_bytes)

		metadata = {
			"url": image_url,
			"width": resized_image.width,
			"height": resized_image.height,
			"apect_ratio": aspect_ratio,
			"format": image_format,
			"file_size": len(resized_image_bytes)
		}

			# Add more metadata fields as needed


		return {
			"metadata": metadata,
			"data": encoded_data
		}
	except Exception as e:
		return {"error": str(e)}

@app.post("/resize/")
async def resize_image(image_url: str):
	try:
		response = requests.get(image_url)
		image_data = BytesIO(response.content)
		image = Image.open(image_data)
		resized_images = {}
		for width in DEFAULT_WIDTHS:
			resized_image = resize_with_aspect(image.copy(), width)
			resized_image_data = BytesIO()
			resized_image.save(resized_image_data, format="WEBP")
			resized_image_bytes = resized_image_data.getvalue()
			encoded_data = base64.b64encode(resized_image_bytes)
			ret = {
				"width": width,
				"data": encoded_data
			}
			resized_images[width] = ret
		return resized_images

	except Exception as e:
		return {"error": str(e)}
