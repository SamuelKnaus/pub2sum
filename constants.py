"""
    Contains project wide constants
"""
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
ALLOWED_FILE_EXTENSIONS = {"pdf", "zip"}
DELIMITER = "/******/"
TEMPORARY_FOLDER = "temp"
INSTRUCTION = "Comprehensively summarize the following scientific text."

DEFAULT_MODEL = "text-davinci-003"
FINE_TUNED_MODEL = "davinci:ft-personal-2023-02-01-12-29-59"