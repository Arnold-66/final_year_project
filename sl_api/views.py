from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from .models import Sign
from .serializers import SignSerializer, SignDetailSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
import os
import json
from django.views import View
from django.http import JsonResponse

# views.py - Updated with debugging
from rest_framework import generics, status
from rest_framework.response import Response
import traceback

class SignListAPIView(generics.ListAPIView):
    """List all signs"""
    serializer_class = SignSerializer
    
    def get_queryset(self):
        try:
            # Log the query
            print("Attempting to fetch signs from database...")
            queryset = Sign.objects.all()
            print(f"Found {queryset.count()} signs")
            return queryset
        except Exception as e:
            print(f"Error in get_queryset: {str(e)}")
            traceback.print_exc()
            raise
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"Error in SignListAPIView.list: {str(e)}")
            traceback.print_exc()
            return Response(
                {'error': str(e), 'detail': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# views.py - Update the SignDetailAPIView
from django.core.files.storage import default_storage

class SignDetailAPIView(APIView):
    """Get sign by word/gloss with SiGML content"""
    def get(self, request, word, format=None):
        # Case-insensitive search, remove underscores/spaces
        cleaned_word = word.strip().lower().replace('_', ' ').replace('-', ' ')
        
        # Try to find the sign (case-insensitive, handle variations)
        sign = Sign.objects.filter(
            Q(word__iexact=cleaned_word) |
            Q(word__iexact=word) |
            Q(word__iexact=word.replace('_', ' '))
        ).first()
        
        if sign:
            # Read SiGML file content
            sigml_content = ""
            try:
                if sign.sigml_file and default_storage.exists(sign.sigml_file.name):
                    with default_storage.open(sign.sigml_file.name, 'r') as f:
                        sigml_content = f.read().decode('utf-8')
            except Exception as e:
                print(f"Error reading SiGML file: {e}")
            
            data = {
                'id': sign.id,
                'word': sign.word,
                'sigml_file_url': request.build_absolute_uri(sign.sigml_file.url) if sign.sigml_file else None,
                'sigml_content': sigml_content,  # Include SiGML content directly
                'created_at': sign.created_at,
                'updated_at': sign.updated_at
            }
            return Response(data)
        
        # Return 404 with JSON response
        return Response(
            {'error': f'Sign for word "{word}" not found'},
            status=status.HTTP_404_NOT_FOUND
        )

def frontend_view(request):
    """Render main page"""
    return render(request, 'frontend.html')

@method_decorator(csrf_exempt, name='dispatch')
class BulkSignUploadView(APIView):
    """Bulk upload signs from a folder"""
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, format=None):
        try:
            folder_path = request.data.get('folder_path', '')
            
            if not folder_path or not os.path.exists(folder_path):
                return Response(
                    {'error': 'Folder path does not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Scan for .sigml files
            sigml_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith('.sigml'):
                        sigml_files.append(os.path.join(root, file))
            
            results = {
                'total_files': len(sigml_files),
                'uploaded': 0,
                'failed': 0,
                'details': []
            }
            
            # Upload each file
            for file_path in sigml_files:
                try:
                    # Extract word from filename
                    filename = os.path.basename(file_path)
                    word = filename.replace('.sigml', '').replace('_', ' ').strip()
                    
                    # Check if sign already exists
                    if Sign.objects.filter(word__iexact=word).exists():
                        results['details'].append({
                            'file': filename,
                            'status': 'skipped',
                            'reason': 'Already exists'
                        })
                        continue
                    
                    # Create new sign
                    with open(file_path, 'rb') as f:
                        sign = Sign(word=word)
                        sign.sigml_file.save(filename, f)
                        sign.save()
                    
                    results['uploaded'] += 1
                    results['details'].append({
                        'file': filename,
                        'status': 'success',
                        'word': word
                    })
                    
                except Exception as e:
                    results['failed'] += 1
                    results['details'].append({
                        'file': os.path.basename(file_path),
                        'status': 'failed',
                        'reason': str(e)
                    })
            
            return Response(results)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GenerateCategoriesView(APIView):
    """Generate categories file from database"""
    
    def get(self, request, format=None):
        try:
            # Get all signs
            signs = Sign.objects.all()
            
            # Create categories
            categories = {
                "Alphabet": [],
                "Greetings": [],
                "Questions": ["what", "where", "when", "why", "how", "who"],
                "Common Words": ["yes", "no", "maybe", "help", "water", "food", "time"],
                "Family": ["mother", "father", "brother", "sister", "family", "friend"],
                "Time": ["today", "tomorrow", "yesterday", "now", "later", "morning"],
                "Basic Needs": ["eat", "drink", "sleep", "work", "home", "school"],
                "Emotions": ["happy", "sad", "angry", "tired", "excited", "scared"],
                "Places": ["house", "school", "work", "store", "hospital", "park"],
                "Actions": ["go", "come", "see", "hear", "talk", "walk", "run"],
                "Descriptions": ["big", "small", "hot", "cold", "good", "bad", "beautiful"],
                "All Signs": []
            }
            
            # Add signs to categories
            for sign in signs:
                word = sign.word.lower()
                categories["All Signs"].append(word)
                
                # Check for letters
                if len(word) == 1 and word.isalpha():
                    categories["Alphabet"].append(word)
                
                # Check for greetings
                greetings = ["hello", "hi", "goodbye", "bye", "thank", "please", "sorry", "welcome"]
                if any(greet in word for greet in greetings):
                    if word not in categories["Greetings"]:
                        categories["Greetings"].append(word)
            
            # Remove empty categories
            categories = {k: v for k, v in categories.items() if v}
            
            # Sort each category
            for category in categories:
                categories[category].sort()
            
            return JsonResponse(categories)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(csrf_exempt, name='dispatch')
class PublicSignUploadView(View):  # Use Django's View instead of DRF's APIView
    """Public API endpoint to upload signs (CSRF exempt)"""
    
    def post(self, request, *args, **kwargs):
        try:
            word = request.POST.get('word', '').strip()
            sigml_file = request.FILES.get('sigml_file')
            
            if not word:
                return JsonResponse(
                    {'error': 'Word/gloss is required'},
                    status=400
                )
            
            if not sigml_file:
                return JsonResponse(
                    {'error': 'SiGML file is required'},
                    status=400
                )
            
            # Check file extension
            if not sigml_file.name.lower().endswith('.sigml'):
                return JsonResponse(
                    {'error': 'File must be a .sigml file'},
                    status=400
                )
            
            # Check if sign already exists (case-insensitive)
            if Sign.objects.filter(word__iexact=word).exists():
                return JsonResponse(
                    {'error': f'Sign "{word}" already exists'},
                    status=409
                )
            
            # Create new sign
            sign = Sign(word=word)
            
            # Save the file
            sign.sigml_file.save(sigml_file.name, sigml_file)
            sign.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Sign "{word}" uploaded successfully',
                'id': sign.id,
                'word': sign.word,
                'file_url': sign.sigml_file.url
            }, status=201)
            
        except Exception as e:
            return JsonResponse(
                {'error': str(e)},
                status=500
            )
# Remove the duplicate SignUploadAPIView at the bottom
# Keep only one version - either use the generic CreateAPIView or the custom APIView
# I recommend using this custom version:

@method_decorator(csrf_exempt, name='dispatch')
class SignUploadAPIView(APIView):
    """API endpoint to upload new signs"""
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        word = request.data.get('word', '').strip()
        sigml_file = request.FILES.get('sigml_file')
        
        if not word:
            return Response(
                {'error': 'Word/gloss is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not sigml_file:
            return Response(
                {'error': 'SiGML file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check file extension
        if not sigml_file.name.lower().endswith('.sigml'):
            return Response(
                {'error': 'File must be a .sigml file'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if sign already exists
        if Sign.objects.filter(word__iexact=word).exists():
            return Response(
                {'error': f'Sign "{word}" already exists'},
                status=status.HTTP_409_CONFLICT
            )
        
        try:
            # Create new sign
            sign = Sign(word=word)
            sign.sigml_file.save(sigml_file.name, sigml_file)
            sign.save()
            
            serializer = SignSerializer(sign)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
# views.py - Add this frontend view
from django.http import HttpResponse
from django.template import loader
import os
from django.conf import settings


def frontend_view(request):
    """Serve the React frontend"""
    try:
        # Check if we have a built React app
        react_index_path = os.path.join(settings.BASE_DIR, 'frontend', 'build', 'index.html')
        if os.path.exists(react_index_path):
            with open(react_index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HttpResponse(content)
        else:
            # Fallback to template
            return render(request, 'frontend.html')
    except:
        return render(request, 'frontend.html')


# views.py - Add debugging
from django.http import JsonResponse
import json
import traceback

def debug_api(request):
    """Debug endpoint to test API issues"""
    debug_info = {
        'request_method': request.method,
        'request_path': request.path,
        'request_headers': dict(request.headers),
    }
    
    try:
        # Test database connection
        from .models import Sign
        sign_count = Sign.objects.count()
        debug_info['sign_count'] = sign_count
        
        # Test serializer
        from .serializers import SignSerializer
        signs = Sign.objects.all()[:3]
        serializer = SignSerializer(signs, many=True, context={'request': request})
        debug_info['serializer_data'] = serializer.data
        debug_info['serializer_success'] = True
        
    except Exception as e:
        debug_info['error'] = str(e)
        debug_info['traceback'] = traceback.format_exc()
        debug_info['serializer_success'] = False
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})




# Add to views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def set_avatar(request):
    """Save user's avatar preference"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            avatar = data.get('avatar', 'anna')
            
            # Save to session
            request.session['selected_avatar'] = avatar
            
            return JsonResponse({
                'success': True,
                'avatar': avatar,
                'message': f'Avatar set to {avatar}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@csrf_exempt
def get_avatar(request):
    """Get user's avatar preference"""
    avatar = request.session.get('selected_avatar', 'anna')
    return JsonResponse({
        'success': True,
        'avatar': avatar
    })