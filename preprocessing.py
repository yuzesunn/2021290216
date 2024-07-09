import json
from sklearn.model_selection import train_test_split


def load_data(json_file_path):
    """加载数据并将其分为真实新闻和假新闻"""
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    original_news = [entry['origin_text'] for entry in data.values()]
    fake_news = [entry['generated_text_glm4'] for entry in data.values()]

    return original_news, fake_news


def create_datasets(original_news, fake_news, test_size=0.2, random_state=42):
    """创建训练集和测试集"""
    # 合并数据和标签
    X = original_news + fake_news
    y = ['real'] * len(original_news) + ['fake'] * len(fake_news)

    # 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    return (X_train, y_train), (X_test, y_test)


# 使用
json_file_path = 'gossipcop_v3-2_content_based_fake.json'
original_news, fake_news = load_data(json_file_path)

(train_data, train_labels), (test_data, test_labels) = create_datasets(original_news, fake_news)


# 打印训练集和测试集的大小
print("Training set size:", len(train_data))
print("Testing set size:", len(test_data))


def write_dataset_to_file(data, labels, filename):
    """将数据集写入文件，确保文本不换行"""
    with open(filename, 'w', encoding='utf-8') as file:
        for text, label in zip(data, labels):
            # 移除文本中的换行符
            clean_text = text.replace('\n', ' ').replace('\r', '')
            file.write(f"{label}\t{clean_text}\n")

# 写入训练集到 train.txt 文件
write_dataset_to_file(train_data, train_labels, 'train.txt')

# 写入测试集到 test.txt 文件
write_dataset_to_file(test_data, test_labels, 'test.txt')
