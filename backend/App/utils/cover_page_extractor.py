import zipfile
from io import BytesIO

import fitz  # PyMuPDF
from PIL import Image
from loguru import logger


class CoverPageExtractor:
    @staticmethod
    def extract_cover_image_from_data(file_data: bytes, extension: str):
        """Returns the cover image as a base64-encoded string."""
        try:
            cover_image = None
            if not file_data:
                raise ValueError("File data cannot be empty")
            if extension == "application/pdf":
                cover_image = CoverPageExtractor.pdf_to_image_from_data(file_data)
            elif extension == "application/epub+zip":
                cover_image = CoverPageExtractor.extract_cover_from_epub(file_data)
            if not cover_image and extension in ["application/pdf", "application/epub+zip"]:
                # Handle fallback if it claimed to be PDF/EPUB but we failed to find one
                try:
                    cover_image = CoverPageExtractor.extract_first_page_as_image(file_data)
                except Exception as inner_e:
                    logger.warning(f"Fallback cover extraction failed: {str(inner_e)}")

            # If no cover image found (or if it's a txt file), returns None
            return cover_image

        except Exception as e:
            logger.error(f"Error extracting cover image: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def pdf_to_image_from_data(file_data: bytes, zoom=2):
        try:
            doc = fitz.open(stream=BytesIO(file_data))
            page = doc.load_page(0)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            buffered = BytesIO()
            image = Image.open(BytesIO(pix.tobytes("png")))
            image.save(buffered, format="PNG")
            return buffered.getvalue()
        except Exception as e:
            logger.error(f"Error extracting PDF cover: {e}")
            raise

    @staticmethod
    def extract_cover_from_epub(file_bytes: bytes):
        try:
            with zipfile.ZipFile(BytesIO(file_bytes), "r") as epub_zip:
                # Search for a cover image within the EPUB zip file
                for file_name in epub_zip.namelist():
                    if "cover" in file_name.lower() and file_name.endswith((".jpg", ".jpeg", ".png")):
                        with epub_zip.open(file_name) as cover_file:
                            return cover_file.read()
        except Exception as e:
            logger.error(f"Error extracting EPUB cover: {e}")
            raise

    @staticmethod
    def extract_first_page_as_image(file_bytes: bytes):
        try:
            # Convert the bytes into a file-like object
            file_stream = BytesIO(file_bytes)

            # Open the document as a file-like object
            doc = fitz.open("pdf", file_stream)  # Open the document as PDF (if it’s a PDF)
            page = doc.load_page(0)  # Render the first page
            pix = page.get_pixmap()  # Convert to pixmap
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)  # Convert to PIL image

            # Save the image to a BytesIO object
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()

        except Exception as e:
            logger.error(f"Error rendering first page as image: {e}")
            raise

    @staticmethod
    def main(book_data, book_type):
        return CoverPageExtractor.extract_cover_image_from_data(book_data, book_type)
