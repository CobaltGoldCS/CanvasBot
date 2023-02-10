from canvasapi import Canvas
from canvasapi.paginated_list import PaginatedList
from canvasapi.assignment import Assignment

from datetime import datetime, timezone, timedelta
from userdata import UserData


def get_current_courses(canvas: Canvas) -> PaginatedList:
    return canvas.get_courses(enrollment_state='active', enrollment_type='student')

def get_assignments_within_period(start: datetime, end: datetime, users: list[UserData]) -> list[Assignment]:
    start_time = start.astimezone(timezone.utc)
    cutoff_time = end.astimezone(timezone.utc)
    assignments = []
    for user in map(lambda user: user.make_canvas(), users):
        for course in get_current_courses(user):
            for assignment in course.get_assignments(order_by='due_at'):
                if not hasattr(assignment, "due_at_date"):
                    assignments.append(assignment)
                    continue
                if (assignment.due_at_date >= start_time and assignment.due_at_date <= cutoff_time):
                    assignments.append(assignment)
    return assignments

    
            