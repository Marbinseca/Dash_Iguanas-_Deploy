# setup.py
from setuptools import setup

setup(
    name="iguanas-dashboard",
    version="1.0.0",
    install_requires=[
        "Flask==2.2.5",
        "pandas==1.4.4",
        "numpy==1.23.5",
        "plotly==5.13.0",
        "gunicorn==20.1.0",
        "python-dotenv==0.21.0",
        "openpyxl==3.0.10",
        "Werkzeug==2.2.3"
    ]
)