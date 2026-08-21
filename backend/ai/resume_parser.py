import os


def extract_resume_text(file_path):
    extension = (
        os.path.splitext(
            file_path
        )[1]
        .lower()
    )

    if extension == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(
            file_path
        )

        text_parts = []

        for page in reader.pages:
            text_parts.append(
                page.extract_text() or ""
            )

        return "\n".join(
            text_parts
        ).strip()

    if extension == ".txt":
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()

    raise ValueError(
        "Unsupported resume format. "
        "Use PDF or TXT."
    )


def parse_resume_text(text):
    if not text or not text.strip():
        return {
            "text": "",
            "skills": [],
        }

    return {
        "text": text.strip(),
        "skills": [],
    }