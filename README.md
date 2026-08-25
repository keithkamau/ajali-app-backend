# Ajali Web application

## Setup Instructions

- Create virtual environment

```
python -m venv venv
```

- Activate virtual environment
  - On Windows:

  ```
  venv\Scripts\activate
  ```

- On macOS/Linux:

  ```
  source venv/bin/activate
  ```

- Install dependencies

  ```
  pip install -r requirements.txt
  ```

- Create .env file with environment variables

- Initialize database

  ```
  flask db init
  flask db migrate -m "Initial migration"
  flask db upgrade
  ```

- Run tests

  ```
  pytest tests/ -v --cov=app
  ```

- Run application

  ```
  python run.py
  ```

- Access API at <http://localhost:5000>
