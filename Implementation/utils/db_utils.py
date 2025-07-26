def model_to_dict(obj):
    return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}
