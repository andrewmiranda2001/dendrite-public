def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
def write_to_file(file_path: str, data: str):
    print(f"!!!!!!!!!!!!!!!!!!Writing to file: {file_path}")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)