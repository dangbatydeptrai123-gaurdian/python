from flask import Flask, request, jsonify
from underthesea import word_tokenize
import re

app = Flask(__name__)

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

# Keywords for sentiment analysis
POSITIVE_KEYWORDS = [
    'tốt', 'hài lòng', 'thích', 'tuyệt', 'ok', 'đẹp', 'hay', 'vui',
    'ổn', 'chất', 'xịn', 'nice', 'yêu', 'perfect', 'rất tốt', 'siêu',
    'hạnh phúc', 'đỉnh', 'mượt', 'ưng', 'tks', 'thanks', 'cảm ơn'
]

NEGATIVE_KEYWORDS = [
    'tệ', 'kém', 'hư', 'lỗi', 'xấu', 'dở', 'chán', 'bực', 'tức',
    'hỏng', 'khiếu nại', 'phàn nàn', 'trục trặc', 'vấn đề', 'ko', 'không',
    'fail', 'sucks', 'hok', 'hong', 'tồi', 'quá tệ', 'gay go'
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
    Analyze sentiment of the message (in Vietnamese).
    Returns 0 for positive, 1 for negative.
    """
    tokens = word_tokenize(message.lower(), format="text").split()
    positive_score = sum(1 for token in tokens if token in POSITIVE_KEYWORDS)
    negative_score = sum(1 for token in tokens if token in NEGATIVE_KEYWORDS)
    
    # Simple scoring: positive if more positive keywords, negative otherwise
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
