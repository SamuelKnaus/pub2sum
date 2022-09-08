"""
    Contains project wide constants
"""

TEMPORARY_FOLDER = "temp"
EXTRACTION_FOLDER = "unzipped"
ALLOWED_EXTENSIONS = {"pdf", "zip"}

LAYOUT_MODEL = "lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config"
EXTRA_CONFIG = ["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
LABEL_MAP = {0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
