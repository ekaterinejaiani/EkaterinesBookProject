from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
BOOKS_FILE = 'books.json'

def load_books():
    if not os.path.exists(BOOKS_FILE):
        with open(BOOKS_FILE, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(BOOKS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_books(books):
    with open(BOOKS_FILE, 'w') as f:
        json.dump(books, f, indent=2)

def find_book_by_id(book_id):
    books = load_books()
    for book in books:
        if book['id'] == book_id:
            return book
    return None

def generate_new_id():
    books = load_books()
    if not books:
        return 1
    return max(book['id'] for book in books) + 1

@app.route('/books', methods=['GET'])
def get_all_books():
    try:
        books = load_books()
        return jsonify({
            'success': True,
            'data': books,
            'message': f'Retrieved {len(books)} books successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving books: {str(e)}'
        }), 500

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    try:
        book = find_book_by_id(book_id)
        if not book:
            return jsonify({
                'success': False,
                'message': f'Book with ID {book_id} not found'
            }), 404
        return jsonify({
            'success': True,
            'data': book,
            'message': 'Book retrieved successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving book: {str(e)}'
        }), 500

@app.route('/books', methods=['POST'])
def add_book():
    try:
        data = request.get_json()
        required_fields = ['title', 'author', 'rate', 'status']
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        try:
            rate = float(data['rate'])
            if rate < 1 or rate > 5:
                return jsonify({
                    'success': False,
                    'message': 'Rate must be between 1 and 5'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Rate must be a valid number'
            }), 400
        new_book = {
            'id': generate_new_id(),
            'title': data['title'].strip(),
            'author': data['author'].strip(),
            'rate': rate,
            'status': data['status'].strip(),
            'created_at': datetime.now().isoformat()
        }
        books = load_books()
        books.append(new_book)
        save_books(books)
        return jsonify({
            'success': True,
            'data': new_book,
            'message': 'Book added successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding book: {str(e)}'
        }), 500

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        books = load_books()
        book_index = None
        for i, book in enumerate(books):
            if book['id'] == book_id:
                book_index = i
                break
        if book_index is None:
            return jsonify({
                'success': False,
                'message': f'Book with ID {book_id} not found'
            }), 404
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        updated_book = books[book_index].copy()
        if 'title' in data:
            updated_book['title'] = data['title'].strip()
        if 'author' in data:
            updated_book['author'] = data['author'].strip()
        if 'rate' in data:
            try:
                rate = float(data['rate'])
                if rate < 1 or rate > 5:
                    return jsonify({
                        'success': False,
                        'message': 'Rate must be between 1 and 5'
                    }), 400
                updated_book['rate'] = rate
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Rate must be a valid number'
                }), 400
        if 'status' in data:
            updated_book['status'] = data['status'].strip()
        updated_book['updated_at'] = datetime.now().isoformat()
        books[book_index] = updated_book
        save_books(books)
        return jsonify({
            'success': True,
            'data': updated_book,
            'message': 'Book updated successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating book: {str(e)}'
        }), 500

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        books = load_books()
        book_to_delete = None
        book_index = None
        for i, book in enumerate(books):
            if book['id'] == book_id:
                book_to_delete = book
                book_index = i
                break
        if book_to_delete is None:
            return jsonify({
                'success': False,
                'message': f'Book with ID {book_id} not found'
            }), 404
        books.pop(book_index)
        save_books(books)
        return jsonify({
            'success': True,
            'data': book_to_delete,
            'message': f'Book "{book_to_delete["title"]}" deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting book: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Book Guide API is running successfully',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    if not os.path.exists(BOOKS_FILE):
        sample_books = [
            {
                'id': 1,
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'rate': 4.2,
                'status': 'read',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 2,
                'title': '1984',
                'author': 'George Orwell',
                'rate': 4.8,
                'status': 'reading in progress',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 3,
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'rate': 4.5,
                'status': 'read',
                'created_at': datetime.now().isoformat()
            }
        ]
        save_books(sample_books)
    app.run(debug=True, host='0.0.0.0', port=5000)


