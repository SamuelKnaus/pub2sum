# Getting Started

This is a summary generator app which can be used to create authentic summaries from scientific literature. It uses
the [Flask](https://flask.palletsprojects.com/en/2.0.x/) web framework together with
the [Layout Parser](https://layout-parser.github.io/) document analysis framework and
the [GPT-3](https://openai.com/api/) language model from OpenAI. Check out the instructions below to get set up.

## Prerequisites

- Linux-based operating system (e.g., MacOS or Ubuntu)
- Python >= 3.10 [ from here](https://www.python.org/downloads/)

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

4. Install the requirements<br/>
   ```bash
   $ cat requirements.txt | xargs -n 1 pip install
   ```

5. Make a copy of the example environment variables file<br/>
   ```bash
   $ cp .env.example .env
   ```

6. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file

7. Run the app<br/>
   ```bash
   $ flask run
   ```

You should now be able to access the app at [http://127.0.0.1:5000](http://127.0.0.1:5000)!