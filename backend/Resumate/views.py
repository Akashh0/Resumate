from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from .resume_parser import extract_resume_text, extract_info, generate_feedback
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
        resume = request.FILES.get('resume')
        if not resume:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        temp_file_path = f'temp_{resume.name}'
        try:
            # Save the uploaded file
            with open(temp_file_path, 'wb+') as f:
                for chunk in resume.chunks():
                    f.write(chunk)

            # Extract raw text
            text = extract_resume_text(temp_file_path)
            if not text or not text.strip():
                raise ValueError("❌ Unable to extract text from the uploaded file.")

            # Analyze resume
            info = extract_info(text)  # Calls HuggingFace NER + regex/keyword rules
            feedback = generate_feedback(text, info)

            # Clean up
            os.remove(temp_file_path)

            return Response({
                "message": "✅ Resume parsed and analyzed successfully",
                "text": text,
                "info": info,
                "score": feedback.get("score", 0),
                "alignment": feedback.get("alignment", ""),
                "feedback": feedback.get("feedback", []),
                "issues": feedback.get("issues", []),
                "positives": feedback.get("positives", []),
                "suggestions": feedback.get("suggestions", []),
                "word_count": info.get("word_count", 0),
                "skills_count": len(info.get("skills", [])),
                "has_github_or_portfolio": info.get("github", False),
                "email_count": len(info.get("email", [])),
                "phone_count": len(info.get("phone", [])),
                "name_found": info.get("name") != "Not Found",
                "education_found": info.get("education") == "Yes"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return Response({"error": f"❌ Resume analysis failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




