from flask import Flask, request, jsonify
from traceback import print_exc
from utils import calc_mood, get_adj, get_image_and_text

app = Flask(__name__)


@app.route('/get_mood')
def get_mood():
    try:
        user_id = request.args.get('user_id') or '1'
        score = list(calc_mood(user_id))
        mood = get_adj(*score)
        image_text = get_image_and_text(mood)
        response = {
            'status': 'success',
            'user_id': str(user_id),
            'score': score,
            'mood': get_adj(*score),
            'image_id': image_text['image'],
            'text': image_text['text']
        }
    except Exception as e:
        print_exc()
        response = {
            'status': 'falied',
            'error': str(e)
        }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=23456)