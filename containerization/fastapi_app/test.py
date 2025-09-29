# # test_main.py
# from fastapi.testclient import TestClient
# from main import app  # your FastAPI app

# client = TestClient(app)

# def test_fill_gap():
#     response = client.get("/exercise/fill-gap")
#     print(response)
#     assert response.status_code == 200
#     data = response.json()
#     assert "original_word" in data
#     assert "masked_word" in data
#     assert "_" in data["masked_word"]

# def test_match_exercise():
#     response = client.get("/exercise/match")
#     assert response.status_code == 200
#     data = response.json()
#     assert "words" in data and isinstance(data["words"], list)
#     assert "definitions" in data and isinstance(data["definitions"], list)
#     assert len(data["words"]) == len(data["definitions"]) == 5


# if __name__ == "__main__":
#     print("Running test_fill_gap...")
#     test_fill_gap()
#     print("test_fill_gap passed.")
#     print("Running test_match_exercise...")
#     test_match_exercise()
#     print("test_match_exercise passed.")