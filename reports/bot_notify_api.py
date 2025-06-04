from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class ReportNotifyBotAPIView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request):
        # Bu viewga signal orqali report ma'lumotlari keladi
        # Aiogram bot polling orqali bu endpointni tekshiradi yoki webhook sifatida ishlatadi
        # request.data = {report_id, reporter, reported, reason, timestamp}
        # Siz bu joyda xabarni Redis, fayl yoki DB ga saqlab, bot polling orqali olib ketishini ham qilishingiz mumkin
        # Hozircha oddiy javob qaytaradi
        return Response({"ok": True}, status=status.HTTP_200_OK)
