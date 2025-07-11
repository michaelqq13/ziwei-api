from setuptools import setup, find_packages

# 從 requirements.txt 讀取依賴
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='ziwei_api',
    version='1.0.0',
    packages=find_packages(),
    
    # 這是關鍵：告訴 setuptools 包含 app/assets/ 中的所有檔案
    # 使用 a* 確保 assets 資料夾被包含
    package_data={
        'app': ['assets/*'],
    },
    
    # 確保 setuptools 將 package_data 包含進來
    include_package_data=True,
    
    # 從 requirements.txt 動態載入依賴
    install_requires=requirements,
    
    # 讓 Railway 可以執行 uvicorn
    entry_points={
        'console_scripts': [
            'run-api=app.main:main',
        ],
    },
) 