def update_user_status(user):
    reviews_count = user.reviews.count()

    if reviews_count >= 10:
        user.role = user.Role.CURATOR
        user.status = user.Status.REVIEWER
        user.save()
