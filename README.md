# Getting Started

This app is a summary generator for scientific literature. It employs
the [Flask web framework](https://flask.palletsprojects.com/en/2.0.x/) in combination with
the [GPT-3](https://openai.com/api/) language model from OpenAI. Please refer to the instructions below to set up the
summarizer.

## Prerequisites

- Python >= 3.10 [from here](https://www.python.org/downloads/)

## Setup

1. Clone this repository<br/>
   ```bash
   $ git clone https://github.com/SamuelKnaus/pub2sum.git
   ```

2. Navigate into the project directory<br/>
   ```bash
   $ cd pub2sum
   ```

3. Create a new virtual environment<br/>
   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

4. Install the necessary requirements<br/>
   ```bash
   $ cat requirements.txt | xargs -n 1 pip install
   ```

5. Create a copy of the example environment variables file<br/>
   ```bash
   $ cp .env.example .env
   ```

6. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file

7. Run the app<br/>
   ```bash
   $ flask run
   ```

You should now be able to access the app at [http://127.0.0.1:5000](http://127.0.0.1:5000)!