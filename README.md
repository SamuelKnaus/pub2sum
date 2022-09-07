# pub2sum Quickstart

This is a summary generator app which can be used to create authentic summaries from scientific literature. It uses the [Flask](https://flask.palletsprojects.com/en/2.0.x/) web framework together with the [Layout Parser](https://layout-parser.github.io/) document analysis framework and the [GPT-3](https://openai.com/api/) language model from OpenAI. Check out the instructions below to get set up.

## Setup

1. Install Python >= 3.10 [ from here](https://www.python.org/downloads/)

2. Clone this repository

3. Navigate into the project directory

   ```bash
   $ cd pub2sum
   ```

4. Create a new virtual environment

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

5. Install the requirements

   ```bash
   $ pip install -r requirements.txt
   ```

6. Make a copy of the example environment variables file

   ```bash
   $ cp .env.example .env
   ```

7. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file

8. Run the app

   ```bash
   $ flask run
   ```

You should now be able to access the app at [http://localhost:5000](http://localhost:5000)!