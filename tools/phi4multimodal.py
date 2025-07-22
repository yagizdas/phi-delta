from typing import ClassVar, Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import base64
import requests
from pathlib import Path
import fitz
from PIL import Image
import io
from config import MAIN_PATH

class ImageDescribeInput(BaseModel):
    
    question: str = Field(description="Asked question about the image")
    image_path: str = Field(description="Path to image file (or PDF)")
    already_encoded: bool = Field(default=False, description="True = image_path is already base64-encoded")
    pdf_page: Optional[int] = Field(default=None, description="If the input is a PDF, specify page number (1-indexed)")


class Phi4MMTool(BaseTool):
    name: ClassVar[str] = "describe_image"
    description: ClassVar[str] = (
        "Analyzes an image or a specific page of a PDF using Phi-4-Multimodal. "
        "Supports answering questions about visual content, including text, layout, and images. "
        "If a PDF is provided, you must specify the page number (1-indexed). "
        "Returns detailed answers or interpretations based on the visual input."
    )
    args_schema: Type[BaseModel] = ImageDescribeInput

    def _run(self, question: str, image_path: str, already_encoded: bool = False, pdf_page: Optional[int] = None) -> str:

        
        image_path = MAIN_PATH + image_path 
        
        if already_encoded:
            b64_image = image_path  # assume already encoded string
        else:
            try:
                path = Path(image_path)
                
                if not path.exists():
                    return f"❌ File {image_path} not found."

                #pdf okuma
                if path.suffix.lower() == ".pdf" and pdf_page is not None:
                    b64_image = self.pdf_page_to_base64(image_path, pdf_page)

                # resim okuma
                elif path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                    with open(image_path, "rb") as img_file:
                        b64_image = base64.b64encode(img_file.read()).decode("utf-8")


                else:
                    return f"❌ Unsupported file type: {path.suffix}"
            except Exception as e:
                return f"❌ Failed to read file: {e}"

        payload = {
            "model": "microsoft/Phi-4-multimodal-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64_image}"
                            }
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post("http://localhost:8002/v1/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"❌ Error querying Phi-4-MM: {str(e)}"

    def pdf_page_to_base64(self, pdf_path: str, page_number: int) -> str:
        
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number - 1)  # 0-indexed
        pix = page.get_pixmap(dpi=100)  # reduce DPI first

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Optional: downscale to ~1024px width for safety
        max_width = 1024
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        img.show()
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

