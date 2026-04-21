from flask import Flask, jsonify
from flask_cors import CORS
from flask import request

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


# Error Handling
# -------------------

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405

@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


def validate_blogpost_data(data):
    if "title" not in data or "content" not in data:
        return False
    if data["title"] == "" or data["content"] == "":
        return False
    return True

@app.route('/api/posts', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Get the new blogpost data from the client
        new_blogpost = request.get_json()

        #validate fields
        if not validate_blogpost_data(new_blogpost):
            return jsonify({"error": "Invalid blogpost data, Title and/or content empty."}), 400

        # Generate a new ID for the blogpost
        new_id: int = max((post['id'] for post in POSTS), default=0) + 1
        new_blogpost['id'] = new_id

        # Add the new post to our list
        POSTS.append(new_blogpost)

        # Return the new post data to the client
        return jsonify(new_blogpost), 201
    else:
        # Handle the GET request
        return jsonify(POSTS)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
