from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Report
from .serializers import ReportSerializer
from users.models import User

class ReportAPIView(APIView):
    def post(self, request):
        reporter_id = request.data.get('reporter')
        reported_id = request.data.get('reported')
        reason = request.data.get('reason')
        if not reporter_id or not reported_id or not reason:
            return Response({'error': 'reporter, reported, and reason are required.'}, status=400)
        try:
            reporter = User.objects.get(telegram_id=reporter_id)
            reported = User.objects.get(telegram_id=reported_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        report = Report.objects.create(reporter=reporter, reported=reported, reason=reason)
        serializer = ReportSerializer(report)
        return Response(serializer.data, status=201)
