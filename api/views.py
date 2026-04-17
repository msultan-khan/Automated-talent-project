from uuid import uuid4

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import RunJobSerializer, StartJobSerializer
from api.state import JOB_STORE
from services.extractor_service import ExtractionError, fetch_and_extract
from services.scoring_service import score_content
from services.search_service import run_search
from services.zoho_service import send_to_zoho


class StartJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StartJobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job_id = uuid4()
        JOB_STORE[job_id] = {
            "status": "created",
            "progress": 0,
            "input": serializer.validated_data,
            "results": [],
            "errors": [],
        }
        return Response({"job_id": str(job_id)}, status=status.HTTP_201_CREATED)


class RunJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RunJobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = serializer.validated_data["job_id"]

        job = JOB_STORE.get(job_id)
        if not job:
            return Response({"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        payload = job["input"]
        job["status"] = "running"
        job["progress"] = 10
        job["results"] = []
        job["errors"] = []

        search_hits = run_search(
            role=payload["role"],
            location=payload["location"],
            keywords=payload["keywords"],
            job_type=payload["job_type"],
            search_scope=payload.get("search_scope", "candidates"),
        )
        job["progress"] = 35

        for hit in search_hits:
            url = hit.get("url", "")
            if not url:
                job["errors"].append("Search hit is missing URL.")
                continue

            try:
                extracted = fetch_and_extract(url=url)
                print(f"Extracted content from {url}: {extracted.get('text', '')[:1000]}...")
            except ExtractionError as exc:
                job["errors"].append(str(exc))
                continue

            scoring = score_content(
                extracted_text=extracted.get("text", ""),
                role=payload["role"],
                location=payload["location"],
                keywords=payload["keywords"],
                search_scope=payload.get("search_scope", "candidates"),
            )
            print(f"Scoring for {url}: {scoring}")
            job["results"].append(
                {
                    "url": extracted["url"],
                    "title": extracted["title"],
                    "snippet": extracted["snippet"],
                    "source_type": hit.get("source_type", payload.get("search_scope", "candidates")),
                    "match_role": scoring["match_role"],
                    "match_location": scoring["match_location"],
                    "score": scoring["score"],
                    "reason": scoring["short_reason"],
                }
            )

        job["progress"] = 85
        zoho_response = send_to_zoho(job["results"])
        job["zoho_sync"] = zoho_response
        job["status"] = "completed"
        job["progress"] = 100

        return Response(
            {
                "job_id": str(job_id),
                "status": job["status"],
                "errors": job["errors"],
                "results": job["results"],
                "zoho": zoho_response,
            },
            status=status.HTTP_200_OK,
        )


class JobStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = JOB_STORE.get(job_id)
        if not job:
            return Response({"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "job_id": str(job_id),
                "status": job["status"],
                "progress": job["progress"],
                "result_count": len(job["results"]),
                "error_count": len(job["errors"]),
            },
            status=status.HTTP_200_OK,
        )
