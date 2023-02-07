"""
    Contains project wide constants
"""
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

ALLOWED_FILE_EXTENSIONS = {"pdf"}
TEMPORARY_FOLDER = "temp"

FIRST_INSTRUCTION = "Comprehensively summarize the following scientific text sections."
FINAL_INSTRUCTION = "Combine the following text summaries to a comprehensive final summary of a scientific paper."

LAYOUT_MODEL = "lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config"
EXTRA_CONFIG = ["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
LABEL_MAP = {0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}