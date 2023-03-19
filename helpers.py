from constants import ALLOWED_FILE_EXTENSIONS

# helper function to see if the uploaded file has a valid format
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_FILE_EXTENSIONS
