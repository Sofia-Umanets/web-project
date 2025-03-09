from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

from pydantic import ValidationError

from data_manager import insert_request
from custom_exceptions import BadRequestException
from request_validators import RequestModel

APPLICATION_URLENCODED = "application/x-www-form-urlencoded"
VALIDATION_ERROR_FORMAT = """
<!DOCTYPE HTML>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Form</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
      integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
      rel="stylesheet" crossorigin="anonymous" />
    <link rel="stylesheet" href="/style.css" />
</head>
<body class="fs-120p ff-sans-serif d-flex flex-column min-vh-100">
  <header class="bgc-green">
    <nav class="navbar navbar-expand-sm">
      <div class="container-fluid">
        <a class="navbar-brand" href="/form">
          <h1 class="text-center fw-bold d-inline-block align-middle">
            Form</h1>
        </a>
        <div class="collapse navbar-collapse show" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <a class="nav-link" title="Form" href="/form#form">Form</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </header>
  <div class="m-auto alert alert-danger" role="alert">{explain}</div>
  <footer class="bgc-green mt-auto p-3">
    <div class="text-center">
      Copyright &copy; <time datetime="2025">2025</time> Arkady DiSkills
    </div>
  </footer>
</body>
</html>
"""

def form_urlencoded(function):
    def inner(self, *args, **kwargs):
        if self.headers["Content-Type"] != APPLICATION_URLENCODED:
            raise BadRequestException("invalid Content-Type")

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            raise BadRequestException("invalid Content-Length")

        content = self.rfile.read(content_length).decode()
        query = {}
        for key, value in parse_qs(content).items():
            query[key] = value if len(value) > 1 else value[0]

        return function(self, *args, query=query, **kwargs)

    return inner

class HTTPHandler(BaseHTTPRequestHandler):
    @form_urlencoded
    def form(self, **kwargs):
        query = kwargs["query"]

        languages = query.get("languages")
        if isinstance(languages, str):
            query["languages"] = [languages]

        if "agree_to_terms" in query:
            query["agree_to_terms"] = True
        else:
            query["agree_to_terms"] = False

        try:
            request = RequestModel(**query)
        except ValidationError as e:
            error = e.errors()[0]
            location, msg = error["loc"][0], error["msg"]
            explain = f"Location: {location}. Description: {msg}"
            content = VALIDATION_ERROR_FORMAT.format(explain=explain).encode()

            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content)
            return

        insert_request(request)

        self.send_response(303)
        self.send_header("Location", "/success.html")
        self.end_headers()

    def do_GET(self):
        if self.path == "/form":
            with open("index.html", "rb") as file:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(file.read())
        elif self.path == "/success.html":
            with open("success.html", "rb") as file:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(file.read())
        else:
            self.send_error(404, "File Not Found: %s" % self.path)

    def do_POST(self):
        if self.path == "/form":
            return self.form()
        raise BadRequestException("invalid URL")

    def handle_error(self, exception):
        content = VALIDATION_ERROR_FORMAT.format(explain=str(exception)).encode()
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content)

    def send_error(self, code, message=None, explain=None):
        if explain:
            content = VALIDATION_ERROR_FORMAT.format(explain=explain).encode()
        else:
            content = VALIDATION_ERROR_FORMAT.format(explain=message).encode()
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content)