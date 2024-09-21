import hashlib 


def generate_fingerprint(data: str) -> str:
    """
    data = "This is an example string to generate a fingerprint."
    print("Fingerprint:", generate_fingerprint(data))
    """
    hash_object = hashlib.sha256() # tạo đối tượng hash SHA-256 

    hash_object.update(data.encode('utf-8')) # update hash object 

    fingerprint = hash_object.hexdigest()

    return fingerprint 


def generate_file_fingerprint(file_path: str) -> str:
    """
    file_path = "example.txt"  # Đường dẫn đến file bạn muốn tạo fingerprint
    print("File Fingerprint:", generate_file_fingerprint(file_path))
    """
    hash_object = hashlib.sha256()

    with open(file_path, 'rb') as file:
        # Đọc file theo từng khối dữ liệu (chunk) để tiết kiệm bộ nhớ 
        for chunk in iter(lambda: file.read(4096), b""):
            hash_object.update(chunk) 
    
    # lấy giá trị hash và chuyển đổi thành hexadecimal 
    fingerprint = hash_object.hexdigest()

    return fingerprint 


def generate_md5(data: str) -> str:
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def generate_sha1(data: str) -> str: 
    return hashlib.sha1(data.encode('utf-8')).hexdigest() 


def generate_sha256(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest() 


# data = "example"

# md5_fingerprint = generate_md5(data)
# sha1_fingerprint = generate_sha1(data)
# sha256_fingerprint = generate_sha256(data)

# print("MD5 Fingerprint:", md5_fingerprint)
# print("SHA-1 Fingerprint:", sha1_fingerprint)
# print("SHA-256 Fingerprint:", sha256_fingerprint)
