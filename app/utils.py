import jwt
from functools import wraps
from flask import request, redirect, url_for, current_app, flash
from wonderwords import RandomWord
import random

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            flash('Token is missing!', 'error')
            return redirect(url_for('main.index'))

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_email = data['email']
        except:
            flash('Token is invalid!', 'error')
            return redirect(url_for('main.index'))

        return f(current_user_email, *args, **kwargs)

    return decorated

def generate_username():
    """Generates a random username using wonderwords."""
    r = RandomWord()
    adjective = r.word(include_parts_of_speech=["adjective"])
    noun = r.word(include_parts_of_speech=["noun"])
    if adjective and noun:
        return f"{adjective.capitalize()}{noun.capitalize()}{random.randint(10, 9999)}"
    else:
        # Fallback in case wonderwords fails
        adjectives = ['Super', 'Hyper', 'Mega', 'Ultra', 'Giga', 'Happy', 'Silly', 'Funny', 'Crazy', 'Cool']
        nouns = ['Panda', 'Tiger', 'Lion', 'Bear', 'Fox', 'Wolf', 'Eagle', 'Shark', 'Dragon', 'Unicorn']
        return f'{random.choice(adjectives)}{random.choice(nouns)}{random.randint(10, 99)}'
