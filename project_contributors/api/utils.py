def check_object_exists(model, **kwargs):
    """
    Check if an object exists in the database based on the given model and lookup parameters.

    Args:
        model: The Django model class to query.
        **kwargs: Lookup parameters to filter the objects.

    Returns:
        The object if found, otherwise None.

    Example:
        # Check if a user with username 'john_doe' exists
        user = check_object_exists(User, username='john_doe')
        if user:
            print("User found:", user)
        else:
            print("User not found")
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None
