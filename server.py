import os
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util
import torch

app = Flask(__name__)

model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
TOP_K = int(os.getenv('TOP_K', 5))


# 헬스체크 — Docker / Gateway 용
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model': 'KR-SBERT-V40K-klueNLI-augSTS'}), 200


# 서비스 내부 통신 전용 (recommendation-svc → ai-svc)
@app.route('/internal/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        user_text  = data.get('user_text')
        challenges = data.get('challenges', [])  # [{ id, text }]

        if not user_text or not challenges:
            return jsonify({'error': 'user_text와 challenges는 필수입니다.'}), 400

        challenge_texts = [c['text'] for c in challenges]
        challenge_ids   = [c['id']   for c in challenges]

        user_emb       = model.encode(user_text, convert_to_tensor=True)
        challenge_embs = model.encode(challenge_texts, convert_to_tensor=True)

        similarities = util.cos_sim(user_emb, challenge_embs)[0]
        k = min(TOP_K, len(challenges))
        top_indices     = torch.topk(similarities, k=k).indices.tolist()
        recommended_ids = [challenge_ids[i] for i in top_indices]

        print(f'[internal/recommend] candidates={len(challenges)}, top_k={k}, result={recommended_ids}')

        return jsonify({'recommended_ids': recommended_ids}), 200

    except Exception as e:
        print(f'[internal/recommend] error: {e}')
        return jsonify({'error': '서버 오류', 'detail': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8086))
    app.run(host='0.0.0.0', port=port)
