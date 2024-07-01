from fastapi.encoders import jsonable_encoder


def encode_input(data) -> dict:
    data = jsonable_encoder(data)
    data = {k: v for k, v in data.items() if (v is not None and v is not "id" and v is not "_id")}
    return data