def filter_or_create(model, _id, title):
    filtered_courses = model.objects.filter(id=_id)
    if not filtered_courses.exists():
        return model.objects.create(id=_id, title=title)
    else:
        if filtered_courses.first().title == "" and title != "":
            filtered_courses.first().title = title
        return filtered_courses.first()
