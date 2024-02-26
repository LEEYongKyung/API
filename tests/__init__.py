def get_api_header(token="test"):
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "token": token
}