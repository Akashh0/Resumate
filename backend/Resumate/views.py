from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from .resume_parser import extract_resume_text
import os

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }, status=status.HTTP_201_CREATED)
        print("❌ Register Error:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })

class UploadResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .resume_parser import extract_resume_text, extract_info, generate_feedback

        resume = request.FILES.get('resume')
        if not resume:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        temp_file_path = f'temp_{resume.name}'
        try:
            with open(temp_file_path, 'wb+') as f:
                for chunk in resume.chunks():
                    f.write(chunk)

            text = extract_resume_text(temp_file_path)
            if not text.strip():
                raise ValueError("Could not extract text from the uploaded file.")

            info = extract_info(text)
            feedback = generate_feedback(text, info)

            os.remove(temp_file_path)

            return Response({
                "message": "Resume parsed and analyzed successfully",
                "text": text,
                "info": info,
                "feedback": feedback
            }, status=status.HTTP_200_OK)

        except Exception as e:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

