from flask import Flask, render_template, request, redirect, url_for
from web.src.new_project import create_project_files
from web.src.manage_projects import get_projects_list, delete_project

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/new_project", methods=["GET"])
def new_project():
    return render_template("new_project.html")

@app.route("/create_project", methods=["POST"])
def create_project():
    title = request.form["title"]
    author = request.form["author"]
    copyright_year = request.form["copyright_year"]

    create_project_files(title, author, copyright_year)

    return f"""<p>Project '{title}' created successfully!</p>
               <a href="/">Return to main menu</a>"""

@app.route("/manage_projects", methods=["GET"])
def manage_projects():
    projects = get_projects_list()
    return render_template("manage_projects.html", projects=projects)

@app.route("/delete_project/<slug>", methods=["POST"])
def delete_project_route(slug):
    if delete_project(slug):
        return redirect(url_for("manage_projects"))
    else:
        # Handle error, e.g., display a message
        return "Error deleting project", 500

if __name__ == "__main__":
    app.run(debug=True)
