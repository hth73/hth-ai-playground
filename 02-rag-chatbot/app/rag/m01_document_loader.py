# --------------------------------------------------
# Import Python Modules
# --------------------------------------------------
from io import BytesIO
import pdfplumber

# --------------------------------------------------
# Document Loader
# --------------------------------------------------
def load_document(file_name: str, file_bytes: bytes) -> str:
    """
    Read a PDF, TXT or Markdown document and return its text content.
    """

    # Get file extension
    file_type = file_name.split(".")[-1].lower()

    # --------------------------------------------------
    # PDF
    # --------------------------------------------------
    if file_type == "pdf":
        text = ""

        # Open PDF from memory
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:

            # Read every page
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    # --------------------------------------------------
    # TXT and Markdown
    # --------------------------------------------------
    elif file_type in ("txt", "md"):
        text = file_bytes.decode("utf-8-sig")

    # --------------------------------------------------
    # Unsupported file type
    # --------------------------------------------------
    else:
        raise ValueError(
            f"Unsupported file type: {file_type}"
        )

    # Return extracted text
    return text.strip()
