from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from .resume_parser import extract_resume_text
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
            with open(temp_file_path, 'wb+') as f:
                for chunk in resume.chunks():
                    f.write(chunk)

            text = extract_resume_text(temp_file_path)
            if not text.strip():
                raise ValueError("Could not extract text from the uploaded file.")

            # Extract info and feedback
            info = extract_info(text)
            feedback = generate_feedback(text, info)

            # === Additional Analysis ===
            issues = []
            score = 100

            # Issue 1: Missing GitHub/Portfolio
            if "github" not in text.lower() and "portfolio" not in text.lower():
                issues.append({
                    "title": "Portfolio or GitHub Link Missing",
                    "type": "critical",
                    "description": "Add a GitHub or portfolio link to highlight your projects."
                })
                score -= 15

            # Issue 2: Resume too short
            word_count = len(text.split())
            if word_count < 150:
                issues.append({
                    "title": "Resume Too Short",
                    "type": "moderate",
                    "description": f"Resume has only {word_count} words. Target 250–500 for better detail."
                })
                score -= 10

            # Issue 3: Missing Education
            if info.get("education") == "Not Found":
                issues.append({
                    "title": "Education Section Missing",
                    "type": "critical",
                    "description": "List your degree, university, and graduation year."
                })
                score -= 15

            # Issue 4: Few Technical Skills
            if len(info.get("skills", [])) < 3:
                issues.append({
                    "title": "Very Few Technical Skills",
                    "type": "moderate",
                    "description": "Mention more tools, languages, or frameworks relevant to your role."
                })
                score -= 10

            # Issue 5: Name not detected
            if info.get("name") == "Not Found":
                issues.append({
                    "title": "Name Not Detected",
                    "type": "low",
                    "description": "Ensure your name is clearly mentioned at the top of your resume."
                })
                score -= 5

            # Alignment prediction
            from .resume_parser import bert_classifier
            labels = ["Software Engineer", "Data Scientist", "Web Developer"]
            result = bert_classifier(text, labels)
            alignment = f"✅ Resume aligns best with **{result['labels'][0]}** ({round(result['scores'][0] * 100, 1)}% confidence)"

            # ✅ Clean up
            os.remove(temp_file_path)

            # Final response
            return Response({
                "message": "Resume parsed and analyzed successfully",
                "text": text,
                "info": info,
                "feedback": feedback,
                "score": max(score, 0),
                "alignment": alignment,
                "issues": issues
            }, status=status.HTTP_200_OK)

        except Exception as e:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



