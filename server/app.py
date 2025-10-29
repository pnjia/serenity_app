from flask import Flask, request, jsonify
from firebase_config import USERS_COLLECTION
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os

app = Flask(_name_)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '605dbd2e7cbf57676d41840537806c5ee1ec6935d8a4a9a94242666416991357')


def create_user(user_data):
    try:
        hashed_password = generate_password_hash(user_data['password'], method='sha256')
        
        new_user = {
            'email': user_data['email'],
            'password': hashed_password,
            'full_name': user_data['full_name'],
            'created_at': datetime.datetime.now()
        }
        
        doc_ref = USERS_COLLECTION.add(new_user)
        return True, doc_ref[1].id
    except Exception as e:
        return False, str(e)


def generate_auth_token(user_id):
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24), 
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    except Exception as e:
        return str(e)


@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')

    if not email or not password or not full_name:
        return jsonify({"message": "Data tidak lengkap."}), 400

    try:
        query = USERS_COLLECTION.where('email', '==', email).limit(1).get()
        if len(query) > 0:
            return jsonify({"message": "Email sudah terdaftar."}), 409 

        success, user_id = create_user(data)
        
        if success:
            return jsonify({
                "message": "Registrasi berhasil!",
                "user_id": user_id,
                "email": email
            }), 201
        else:
            return jsonify({"message": "Gagal menyimpan data.", "error": user_id}), 500

    except Exception as e:
        return jsonify({"message": "Terjadi kesalahan server."}), 500


@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email atau password tidak boleh kosong."}), 400

    try:
        query = USERS_COLLECTION.where('email', '==', email).limit(1).get()

        if not query:
            return jsonify({"message": "Email atau password salah."}), 401 
        
        user_doc = query[0]
        user_data = user_doc.to_dict()

        if check_password_hash(user_data['password'], password):
            token = generate_auth_token(user_doc.id)
            
            return jsonify({
                "message": "Login berhasil!",
                "token": token,
                "full_name": user_data['full_name']
            }), 200
        else:
            return jsonify({"message": "Email atau password salah."}), 401

    except Exception as e:
        return jsonify({"message": "Terjadi kesalahan server."}), 500


@app.route('/')
def home():
    return "Server Serenity Aktif! (Backend Python)"

if _name_ == '_main_':
    app.run(debug=True, port=5000)