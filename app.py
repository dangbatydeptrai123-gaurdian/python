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
    'shop', 'hàng', 'deal', 'sale', 'freeship', 'ship', 'oder',  # Teen code/slang
    'mún', 'muh', 'mua sắm', 'check hàng', 'chốt đơn', 'hủy đơn'  # Informal/teen code
]

# Additional context words to improve relevance detection, including teen code
CONTEXT_KEYWORDS = [
    'hỏi', 'muốn', 'cần', 'tìm', 'về', 'liên quan', 'gặp', 'vấn đề', 'lỗi',
    'hok', 'hong', 'kím', 'zề', 'hư', 'fail', 'bug', 'sao', 'nào',  # Teen code/slang
    'check', 'inbox', 'rep', 'rì', 'cmt', 'comment', 'dm'  # Social media slang
]

def is_retail_related(message):
    """
    Check if the message is related to retail problems (in Vietnamese) using NLP.
    Returns 0 for relevant (non-spam), 1 for irrelevant (spam).
    """
    # Tokenize the message using underthesea
    tokens = word_tokenize(message.lower(), format="text").split()
    
    # Check for retail-related keywords
    retail_score = sum(1 for token in tokens if token in RETAIL_KEYWORDS)
    
    # Check for context keywords to boost relevance
    context_score = sum(1 for token in tokens if token in CONTEXT_KEYWORDS)
    
    # Simple scoring: message is relevant if it contains at least one retail keyword
    # or a combination of retail and context keywords
    if retail_score > 0 or (retail_score + context_score >= 2):
        return 0  # Relevant (non-spam)
    return 1  # Irrelevant (spam)

@app.route('/check_message', methods=['POST'])
def check_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Không có tin nhắn được cung cấp'}), 400
    
    message = data['message']
    result = is_retail_related(message)
    return jsonify({'is_spam': result})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)