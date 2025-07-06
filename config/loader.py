import os
import yaml

def load_config():
    # 현재 파일이 있는 디렉토리의 절대 경로를 구함
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'application.yaml')

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


if __name__ == '__main__':
    load_config()