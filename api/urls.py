from django.urls import path

from api.views import JobStatusView, RunJobView, StartJobView

urlpatterns = [
    path("start-job/", StartJobView.as_view(), name="start-job"),
    path("run-job/", RunJobView.as_view(), name="run-job"),
    path("job-status/<uuid:job_id>/", JobStatusView.as_view(), name="job-status"),
]
