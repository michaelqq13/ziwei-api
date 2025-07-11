from setuptools import setup, find_packages

setup(
    name='ziwei_api',
    version='1.0.0',
    packages=find_packages(),
    
    # 這是關鍵：告訴 setuptools 包含 app/assets/ 中的所有檔案
    package_data={
        'app': ['assets/**'],
    },
    
    # 確保 setuptools 將 package_data 包含進來
    include_package_data=True,
    
    # 這裡可以添加其他依賴，但我們先專注於資源檔案
    install_requires=[
        # 這裡的列表應該和 requirements.txt 保持一致
        # 例如: 'fastapi', 'uvicorn', 'sqlalchemy', 'pillow', ...
    ],
    
    # 讓 Railway 可以執行 uvicorn
    entry_points={
        'console_scripts': [
            'run-api=app.main:main',
        ],
    },
) 