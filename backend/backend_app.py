from typing import Tuple, Dict, List

from flask import Flask, jsonify
from flask_cors import CORS
from flask import request

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {
        "id": i,
        "title": f"Post {i}",
        "content": f"Content for post {i}."
    }
    for i in range(1, 101)  # 100 posts
]

# -------------------
# Helper Functions
# -------------------

def validate_blogpost_data(data):
    """
    Validates the blogpost data.

    :param data: data to validate.
    """
    if "title" not in data or "content" not in data:
        return False
    if data["title"] == "" or data["content"] == "":
        return False
    return True

def get_post_by_id(post_id) -> Tuple[int, Dict] | Tuple[None, None]:
    """
    Gets the post by the id.

    :param post_id: id to search for in the list of blogposts.
    :return: Returns the post index in the blog_posts list and the post dictionary.


    """
    for i, post in enumerate(POSTS):
        if post["id"] == post_id:
            return i, post
    return None, None


def sort_posts(sort, direction) -> List[Dict]:
    """
    Returns a sorted list of posts. Returns error code 400 when given invalid parameters.

    :param sort: sort direction. Either "title" or "content".
    :param direction: sort direction. Either "asc" or "desc".
    """

    if sort and direction == "asc":
        return sorted(POSTS, key=lambda post: post[sort], reverse=False)
    if sort and direction == "desc":
        return sorted(POSTS, key=lambda post: post[sort], reverse=True)
    if not sort and direction == "desc":
        return list(reversed(POSTS))
    else:
        return POSTS

# -------------------
# Error Handling
# -------------------

@app.errorhandler(400)
def not_found_error(error):
    return jsonify({"error": "Bad Request"}), 400

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405

# -------------------
# Routes
# -------------------
@app.route('/api/posts', methods=['GET'])
def get_posts():

    # initialize pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    start_index = (page - 1) * limit
    end_index = start_index + limit

    # initialize sorting
    sort = request.args.get('sort')
    direction = request.args.get('direction')
    if sort and sort not in {"title", "content"}:
        return f'Bad Request: sort was given:{sort}, but allows only title or content', 400
    if direction and direction not in {"asc", "desc"}:
        return f'Bad Request: direction was given:{direction}, but allows only asc or desc', 400

    sorted_posts = sort_posts(sort, direction)
    paginated_posts = sorted_posts[start_index:end_index]

    return jsonify(paginated_posts)

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


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    # Find the post with the given ID
    _, post = get_post_by_id(id)

    # If the book wasn't found, return a 404 error
    if post is None:
        return f'Post with id {id} Not Found', 404

    # Remove the post from the list
    POSTS.remove(post)
    return jsonify({"message": f"Post with id {id} has been deleted successfully."})

@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    i, post = get_post_by_id(id)
    if post is None:
        return f'Post with id {id} Not Found', 404

    new_data = request.get_json()
    post["title"] = new_data.get("title", post["title"])
    post["content"] = new_data.get("content", post["content"])

    return jsonify(post), 200

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get('title')
    content = request.args.get('content')

    search_results = []
    if title:
        search_results += [post for post in POSTS if (post not in search_results) and (title in post.get('title'))]
    if content:
        search_results += [post for post in POSTS if (post not in search_results) and (title in post.get('content'))]

    return jsonify(search_results)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
