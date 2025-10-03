from flask import Flask, request, jsonify
from underthesea import word_tokenize
import re
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your actual Gemini API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0')  # Adjust to the correct Gemini 2.0 model name

# Vietnamese keywords related to retail problems, including teen code
RETAIL_KEYWORDS = [
    'mua', 'đặt hàng', 'đơn hàng', 'khiếu nại', 'phàn nàn',
    'giảm giá', 'ưu đãi', 'giá', 'sản phẩm', 'mặt hàng',
    'trả hàng', 'hoàn tiền', 'giao hàng', 'vận chuyển', 'cửa hàng',
    'khách hàng', 'dịch vụ', 'chất lượng', 'tồn kho', 'có sẵn',
    'shop', 'hàng', 'deal', 'sale', 'freeship', 'ship', 'oder',
    'mún', 'muh', 'mua sắm', 'check hàng', 'chốt đơn', 'hủy đơn'
]

# Additional context words to improve relevance detection, including teen code
CONTEXT_KEYWORDS = [
    'hỏi', 'muốn', 'cần', 'tìm', 'về', 'liên quan', 'gặp', 'vấn đề', 'lỗi',
    'hok', 'hong', 'kím', 'zề', 'hư', 'fail', 'bug', 'sao', 'nào',
    'check', 'inbox', 'rep', 'rì', 'cmt', 'comment', 'dm'
]

def is_retail_related(message):
    """
    Check if the message is related to retail problems (in Vietnamese) using NLP.
    Returns 0 for relevant (non-spam), 1 for irrelevant (spam).
    """
    tokens = word_tokenize(message.lower(), format="text").split()
    retail_score = sum(1 for token in tokens if token in RETAIL_KEYWORDS)
    context_score = sum(1 for token in tokens if token in CONTEXT_KEYWORDS)
    if retail_score > 0 or (retail_score + context_score >= 2):
        return 0  # Relevant (non-spam)
    return 1  # Irrelevant (spam)

def analyze_sentiment(message):
    """
    Analyze sentiment of the message (in Vietnamese) using Gemini API.
    Returns 0 for positive, 1 for negative.
    """
    try:
        # Construct prompt for Gemini to analyze sentiment in Vietnamese
        prompt = f'''
        Phân tích cảm xúc của câu sau bằng tiếng Việt: "{message}"
        Xác định cảm xúc là tích cực hay tiêu cực. Trả về chỉ một từ: 'tích cực' hoặc 'tiêu cực'.
        '''


        response = model.generate_content(prompt)
        sentiment = response.text.strip().lower()
        return 1 if sentiment == 'tiêu cực' else 0
    except Exception as e:
        # Fallback to keyword-based sentiment analysis in case of API failure
        tokens = word_tokenize(message.lower(), format="text").split()
        positive_score = sum(1 for token in tokens if token in [
            'tốt', 'hài lòng', 'thích', 'tuyệt', 'ok', 'đẹp', 'hay', 'vui',
            'ổn', 'chất', 'xịn', 'nice', 'yêu', 'perfect', 'rất tốt', 'siêu',
            'hạnh phúc', 'đỉnh', 'mượt', 'ưng', 'tks', 'thanks', 'cảm ơn'
        ])
        negative_score = sum(1 for token in tokens if token in [
            'tệ', 'kém', 'hư', 'lỗi', 'xấu', 'dở', 'chán', 'bực', 'tức',
            'hỏng', 'khiếu nại', 'phàn nàn', 'trục trặc', 'vấn đề', 'ko', 'không',
            'fail', 'sucks', 'hok', 'hong', 'tồi', 'quá tệ', 'gay go'
        ])
        if positive_score > negative_score:
            return 0  # Positive
        return 1  # Negative (or neutral, default to negative for complaints)

@app.route('/check_message', methods=['POST'])
def check_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Không có tin nhắn được cung cấp'}), 400
    
    message = data['message']
    result = is_retail_related(message)
    return jsonify({'is_spam': result})

@app.route('/check_sentiment', methods=['POST'])
def check_sentiment():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Không có tin nhắn được cung cấp'}), 400
    
    message = data['message']
    result = analyze_sentiment(message)
    return jsonify({'is_negative': result})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
