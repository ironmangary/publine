from flask import Flask, render_template, request, redirect, url_for
import os
import sys

# Optional: Add publine/ to sys.path so you can import from core/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

