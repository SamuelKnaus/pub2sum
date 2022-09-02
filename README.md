# Summary Creator Quickstart

This is a summary generator app used for creating authentic summaries for scientific literature. It uses the [Flask](https://flask.palletsprojects.com/en/2.0.x/) web framework together with the [Layout Parser](https://layout-parser.github.io/) document analysis framework and the [GPT-3](https://openai.com/api/) language model from OpenAI. Check out the instructions below to get set up.

## Setup

1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/)

2. If you don't have Tesseract installed, [install it like shown here](https://tesseract-ocr.github.io/tessdoc/Installation.html)

3. Clone this repository

4. Navigate into the project directory

   ```bash
   $ cd OpenAPI
   ```

5. Create a new virtual environment

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

6. Install the requirements

   ```bash
   $ pip install -r requirements.txt
   ```

7. Make a copy of the example environment variables file

   ```bash
   $ cp .env.example .env
   ```

8. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file

9. Run the app

   ```bash
   $ flask run
   ```

You should now be able to access the app at [http://localhost:5000](http://localhost:5000)!
