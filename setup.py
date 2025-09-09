import setuptools

setuptools.setup(
    name='diarrhea',
    version="0.0.1",
    description=(
        'Diarrhea is a chatbot. Behind it is a powerful AI framework architected '
        'to read/write to a relational memory database, and use that ability to '
        'be a powerful diary and chatbot through the use of two different MCPs '
        'with two fine-tuned models.'
    ),
    url='https://github.com/Madiba-SNAP-Labs/SNAP-MCP',
    author='Andrew Miranda',
    author_email='andrewmmiranda01@gmail.com',
    install_requires=[
        'openai',
        'anthropic==0.49.0',
        'mcp[cli]>=1.6.0',
        'pydantic',
        'openai==1.78.1',
        'myers==1.0.1'
    ],
    packages=setuptools.find_packages(include=["*"]),
    package_data={},
    zip_safe=False
)