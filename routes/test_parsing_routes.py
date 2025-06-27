from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, storage
import base64
import io
import uuid
import json
from datetime import datetime
import os
import tempfile
import re
import logging

# PDF processing
try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed. Install with: pip install PyMuPDF")

# NLP components for topic modeling
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
except ImportError:
    print("NLTK not installed. Install with: pip install nltk")

# OpenAI for advanced text processing
try:
    from openai import OpenAI
except ImportError:
    print("OpenAI API not installed. Install with: pip install openai")

# Try to import from our initialization module
try:
    from db_init import db
except ImportError:
    # If import fails, initialize Firebase here
    if not firebase_admin._apps:
        cred = credentials.Certificate('service_key.json')
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'bxscioly-455318.appspot.com'
        })
    db = firestore.client()

# Get Firebase Storage bucket
bucket = storage.bucket('bxscioly-455318.appspot.com')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint
test_parsing_routes = Blueprint('test_parsing_routes', __name__)

# Initialize NLTK resources if needed
def initialize_nltk():
    """Download required NLTK data"""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
        
    # Add punkt_tab resource
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')

# Initialize OpenAI API
def initialize_openai():
    """Initialize OpenAI API with key from environment or api_keys.json"""
    api_key = None
    
    # Try environment variable first
    if os.environ.get('OPENAI_API_KEY'):
        api_key = os.environ.get('OPENAI_API_KEY')
    else:
        # Try to load from api_keys.json
        try:
            with open('api_keys.json', 'r') as f:
                keys = json.load(f)
                api_key = keys.get('OpenAiAPIKey')
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
    
    if api_key:
        return OpenAI(api_key=api_key)
    else:
        logger.warning("OpenAI API key not found in environment variables or api_keys.json")
        return None

# Process PDF document
def process_pdf(pdf_path):
    """Extract text and image info from a PDF file"""
    try:
        doc = fitz.open(pdf_path)
        result = {
            'pages': [],
            'images': [],
            'page_count': len(doc)
        }
        
        # Process each page
        for page_num, page in enumerate(doc):
            # Extract text
            text = page.get_text()
            
            # Get images
            image_list = page.get_images(full=True)
            page_images = []
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Create a unique filename
                image_id = f"pg{page_num+1}_img{img_index+1}"
                image_ext = base_image["ext"]
                image_filename = f"{image_id}.{image_ext}"
                
                # Save position information
                image_info = {
                    'id': image_id,
                    'filename': image_filename,
                    'page': page_num + 1,
                    'width': base_image["width"],
                    'height': base_image["height"],
                    'ext': image_ext
                }
                
                page_images.append(image_info)
                result['images'].append({**image_info, 'data': base64.b64encode(image_bytes).decode('utf-8')})
            
            # Add page data
            result['pages'].append({
                'number': page_num + 1,
                'text': text,
                'images': page_images
            })
        
        return result
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise

# Identify questions in the document using GPT-4o-mini
def extract_questions(pdf_data, event_name):
    """Use GPT-4o-mini to identify and segment individual questions from the document"""
    try:
        # Initialize OpenAI client
        client = initialize_openai()
        if not client:
            raise ValueError("OpenAI client not initialized - API key required")
        
        # Combine all text from pages
        full_text = ""
        page_boundaries = {}
        current_pos = 0
        
        for page in pdf_data['pages']:
            page_text = page['text'].strip()
            if page_text:
                page_boundaries[current_pos] = page['number']
                full_text += f"\n--- PAGE {page['number']} ---\n{page_text}\n"
                current_pos = len(full_text)
        
        # Create a prompt for GPT-4o-mini to segment questions
        system_prompt = f"""You are an expert at analyzing Science Olympiad test documents for the event "{event_name}". 

Your task is to:
1. Identify and segment individual questions from the provided text and images
2. Extract each question's full text (including any sub-parts, multiple choice options, etc.)
3. Determine which page each question appears on
4. Assign relevant topic labels to each question (2-5 topics)
5. Identify questions that include or reference visual elements

You will receive both text content and images from the test document. Use both to accurately identify questions and their characteristics.

Guidelines:
- Questions may be numbered (1, 2, 3...) or lettered (A, B, C...)
- Include all parts of multi-part questions in the text
- For multiple choice questions, include all answer choices
- Topics should be specific to {event_name} (e.g., for Biology: "Cell Structure", "Genetics", "Ecology")
- Set has_diagram to true if the question references figures, diagrams, images, charts, tables, or any visual elements you can see in the provided images
- If you can't determine a clear question boundary, err on the side of keeping related content together
- Use the page markers in the text to determine correct page numbers
- When you see visual content in the images, incorporate that information into your analysis"""

        # Define the JSON schema for structured outputs
        question_schema = {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "number": {
                                "type": "integer",
                                "description": "The question number"
                            },
                            "text": {
                                "type": "string",
                                "description": "The full question text including all parts and options"
                            },
                            "page": {
                                "type": "integer",
                                "description": "The page number where the question appears"
                            },
                            "topics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of 2-5 relevant topic labels for this question"
                            },
                            "has_diagram": {
                                "type": "boolean",
                                "description": "True if the question references or includes figures, diagrams, images, or visual elements"
                            }
                        },
                        "required": ["number", "text", "page", "topics", "has_diagram"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["questions"],
            "additionalProperties": False
        }

        # Prepare messages with both text and images
        messages = [{"role": "system", "content": system_prompt}]
        
        # Create user message with text and images
        user_message = {
            "role": "user",
            "content": []
        }
        
        # Add text content
        user_message["content"].append({
            "type": "text",
            "text": f"Please analyze this {event_name} test document and extract all questions:\n\n{full_text}"
        })
        
        # Add images if they exist (limit to first 10 images to avoid token limits)
        image_count = 0
        max_images = 10
        for image_data in pdf_data['images']:
            if image_count >= max_images:
                break
            
            # Add image to the message
            user_message["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{image_data['ext']};base64,{image_data['data']}",
                    "detail": "low"  # Use low detail to save tokens
                }
            })
            image_count += 1
        
        messages.append(user_message)

        try:
            # Call GPT-4o-mini with structured outputs
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.1,
                max_tokens=4000,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "question_extraction",
                        "schema": question_schema,
                        "strict": True
                    }
                }
            )
            
            # Parse the structured response
            content = response.choices[0].message.content.strip()
            response_data = json.loads(content)
            questions_data = response_data.get('questions', [])
            
            # Validate and format the questions
            questions = []
            for i, q_data in enumerate(questions_data):
                question = {
                    'id': str(uuid.uuid4()),
                    'number': q_data.get('number', i + 1),
                    'text': q_data.get('text', '').strip(),
                    'page': q_data.get('page', 1),
                    'topics': q_data.get('topics', []),
                    'has_diagram': q_data.get('has_diagram', False),
                    'images': []  # Will be populated if we have images on the same page
                }
                
                # Add images from the same page
                for page in pdf_data['pages']:
                    if page['number'] == question['page']:
                        question['images'] = [img['id'] for img in page['images']]
                        break
                
                questions.append(question)
            
            logger.info(f"GPT-4o-mini successfully extracted {len(questions)} questions")
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse structured GPT response as JSON: {e}")
            logger.error(f"Response content: {content}")
            raise ValueError("GPT-4o-mini returned invalid structured response")
            
        except Exception as e:
            logger.error(f"Error calling GPT-4o-mini with structured outputs: {e}")
            raise
    
    except Exception as e:
        logger.error(f"Error extracting questions with GPT-4o-mini: {str(e)}")
        raise

# Topic classification is now handled directly in extract_questions function
# This function is kept for backward compatibility but just returns the questions unchanged
def classify_question_topics(questions, event_name):
    """Topic classification is now handled in extract_questions - this is a no-op for compatibility"""
    return questions

# Create a knowledge graph from the parsed questions
def create_knowledge_graph(questions, event_name):
    """Create a graph of related topics and concepts"""
    try:
        # Extract all topics
        all_topics = set()
        topic_questions = {}
        topic_connections = {}
        
        for question in questions:
            topics = question['topics']
            for topic in topics:
                all_topics.add(topic)
                
                # Track questions for each topic
                if topic not in topic_questions:
                    topic_questions[topic] = []
                topic_questions[topic].append(question['id'])
                
                # Track connections between topics
                for other_topic in topics:
                    if topic != other_topic:
                        if topic not in topic_connections:
                            topic_connections[topic] = {}
                        
                        if other_topic not in topic_connections[topic]:
                            topic_connections[topic][other_topic] = 0
                        
                        topic_connections[topic][other_topic] += 1
        
        # Create graph structure
        nodes = []
        edges = []
        
        # Add nodes for each topic
        for topic in all_topics:
            question_count = len(topic_questions.get(topic, []))
            nodes.append({
                'id': topic,
                'label': topic,
                'size': question_count,
                'question_count': question_count
            })
        
        # Add edges between connected topics
        for source, targets in topic_connections.items():
            for target, weight in targets.items():
                edges.append({
                    'source': source,
                    'target': target,
                    'weight': weight
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'event': event_name
        }
    except Exception as e:
        logger.error(f"Error creating knowledge graph: {str(e)}")
        raise

# Routes
@test_parsing_routes.route('/api/parse-test', methods=['POST'])
def parse_test():
    """Parse a test PDF to extract questions and topics"""
    try:
        # Get JSON data from the request
        request_data = request.json
        
        if not request_data:
            return jsonify({"error": "No data provided"}), 400
        
        test_id = request_data.get('testId')
        event_name = request_data.get('eventName')
        
        if not test_id or not event_name:
            return jsonify({"error": "Missing required fields: testId or eventName"}), 400
        
        # Get the test document from Firestore
        test_doc = db.collection('Tests').document(test_id).get()
        
        if not test_doc.exists:
            return jsonify({"error": "Test not found"}), 404
        
        # Get test data
        test_data = test_doc.to_dict()
        file_url = test_data.get('fileUrl')
        
        if not file_url:
            return jsonify({"error": "Test file not found"}), 404
        
        # Extract the blob name from the URL
        # Handle both Firebase Storage URLs and direct download URLs
        if '//storage.googleapis.com/' in file_url:
            # Direct download URL format
            blob_name = file_url.split('//storage.googleapis.com/')[1].split('/', 1)[1]
        elif 'firebasestorage.googleapis.com' in file_url:
            # Firebase storage URL format
            if '/o/' in file_url:
                blob_name = file_url.split('/o/')[1]
                # Remove query parameters if present
                if '?' in blob_name:
                    blob_name = blob_name.split('?')[0]
            else:
                # Try to get just the filename part as fallback
                blob_name = file_url.split('/')[-1]
                # Remove query parameters if present
                if '?' in blob_name:
                    blob_name = blob_name.split('?')[0]
        else:
            # Fallback to just using the file name
            blob_name = file_url.split('/')[-1]
            # Remove query parameters if present
            if '?' in blob_name:
                blob_name = blob_name.split('?')[0]
        
        # URL decode the blob name if needed
        blob_name = blob_name.replace('%2F', '/')
        
        # Download the PDF from Storage
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_path = temp_file.name
            
            # Download to the temp file
            blob = bucket.blob(blob_name)
            blob.download_to_filename(temp_path)
        
        # Process the PDF
        try:
            # Extract text and images
            pdf_data = process_pdf(temp_path)
            
            # Extract questions with topics (using GPT-4o-mini)
            questions_with_topics = extract_questions(pdf_data, event_name)
            
            # Create knowledge graph
            knowledge_graph = create_knowledge_graph(questions_with_topics, event_name)
            
            # Create a ParsedTest document
            parsed_test = {
                'testId': test_id,
                'eventName': event_name,
                'parsedAt': firestore.SERVER_TIMESTAMP,
                'questionCount': len(questions_with_topics),
                'questions': questions_with_topics,
                'knowledgeGraph': knowledge_graph
            }
            
            # Save to Firebase
            doc_ref = db.collection('ParsedTests').document()
            doc_ref.set(parsed_test)
            
            # Clean up the temp file
            os.unlink(temp_path)
            
            # Return the ID and basic info
            return jsonify({
                "id": doc_ref.id,
                "questionCount": len(questions_with_topics),
                "message": "Test parsed successfully"
            }), 201
            
        except Exception as e:
            # Clean up the temp file in case of error
            try:
                os.unlink(temp_path)
            except:
                pass
            raise e
    
    except Exception as e:
        logger.error(f"Error parsing test: {str(e)}")
        return jsonify({"error": str(e)}), 500

@test_parsing_routes.route('/api/parsed-tests', methods=['GET'])
def get_parsed_tests():
    """Get all parsed tests, optionally filtered by event"""
    try:
        event_name = request.args.get('event')
        
        # Query the ParsedTests collection
        query = db.collection('ParsedTests')
        
        if event_name:
            query = query.where('eventName', '==', event_name)
        
        docs = query.stream()
        items = [{doc.id: doc.to_dict()} for doc in docs]
        
        return jsonify(items), 200
    except Exception as e:
        logger.error(f"Error getting parsed tests: {str(e)}")
        return jsonify({"error": str(e)}), 500

@test_parsing_routes.route('/api/parsed-tests/<parsed_test_id>', methods=['GET'])
def get_parsed_test(parsed_test_id):
    """Get a specific parsed test"""
    try:
        doc = db.collection('ParsedTests').document(parsed_test_id).get()
        
        if not doc.exists:
            return jsonify({"error": "Parsed test not found"}), 404
        
        return jsonify({doc.id: doc.to_dict()}), 200
    except Exception as e:
        logger.error(f"Error getting parsed test: {str(e)}")
        return jsonify({"error": str(e)}), 500

@test_parsing_routes.route('/api/parsed-tests/<parsed_test_id>/knowledge-graph', methods=['GET'])
def get_knowledge_graph(parsed_test_id):
    """Get the knowledge graph for a specific parsed test"""
    try:
        doc = db.collection('ParsedTests').document(parsed_test_id).get()
        
        if not doc.exists:
            return jsonify({"error": "Parsed test not found"}), 404
        
        test_data = doc.to_dict()
        knowledge_graph = test_data.get('knowledgeGraph', {})
        
        return jsonify(knowledge_graph), 200
    except Exception as e:
        logger.error(f"Error getting knowledge graph: {str(e)}")
        return jsonify({"error": str(e)}), 500

@test_parsing_routes.route('/api/parsed-tests/<parsed_test_id>/questions', methods=['GET'])
def get_parsed_questions(parsed_test_id):
    """Get all questions from a parsed test"""
    try:
        doc = db.collection('ParsedTests').document(parsed_test_id).get()
        
        if not doc.exists:
            return jsonify({"error": "Parsed test not found"}), 404
        
        test_data = doc.to_dict()
        questions = test_data.get('questions', [])
        
        return jsonify(questions), 200
    except Exception as e:
        logger.error(f"Error getting parsed questions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@test_parsing_routes.route('/api/generate-study-materials', methods=['POST'])
def generate_study_materials():
    """Generate study materials based on parsed test questions"""
    try:
        request_data = request.json
        
        if not request_data:
            return jsonify({"error": "No data provided"}), 400
        
        parsed_test_id = request_data.get('parsedTestId')
        user_id = request_data.get('userId')
        
        if not parsed_test_id or not user_id:
            return jsonify({"error": "Missing required fields: parsedTestId or userId"}), 400
        
        # Get the parsed test data
        doc = db.collection('ParsedTests').document(parsed_test_id).get()
        
        if not doc.exists:
            return jsonify({"error": "Parsed test not found"}), 404
        
        test_data = doc.to_dict()
        questions = test_data.get('questions', [])
        event_name = test_data.get('eventName')
        
        # Group questions by topic
        topics_questions = {}
        
        for question in questions:
            for topic in question.get('topics', []):
                if topic not in topics_questions:
                    topics_questions[topic] = []
                topics_questions[topic].append(question)
        
        # Create a new binder
        binder_data = {
            'userId': user_id,
            'title': f"{event_name} Study Guide",
            'eventName': event_name,
            'description': f"Automatically generated study materials based on test analysis",
            'sections': [],
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': None,
            'sourceTestId': test_data.get('testId'),
            'sourceParsedTestId': parsed_test_id
        }
        
        # Create sections for the binder
        section_index = 0
        
        # Add overview section
        binder_data['sections'].append({
            'title': 'Overview',
            'order': section_index
        })
        section_index += 1
        
        # Add a section for each topic
        for topic, topic_questions in topics_questions.items():
            binder_data['sections'].append({
                'title': topic,
                'order': section_index,
                'questionCount': len(topic_questions)
            })
            section_index += 1
        
        # Save the binder to Firestore
        binder_ref = db.collection('Binders').document()
        binder_ref.set(binder_data)
        
        # Generate content for each section and save to Storage
        overview_content = f"""
        <h1>{event_name} Study Guide</h1>
        <p>This study guide was automatically generated based on test analysis. It contains the following topics:</p>
        <ul>
        {"".join(f"<li>{topic} ({len(questions)} questions)</li>" for topic, questions in topics_questions.items())}
        </ul>
        <p>Use this guide to focus your study efforts on the most important topics for this event.</p>
        """
        
        # Save overview content
        overview_blob = bucket.blob(f"binders/{binder_ref.id}/Overview.html")
        overview_blob.upload_from_string(overview_content, content_type='text/html')
        
        # For each topic, generate topic content
        for topic, topic_questions in topics_questions.items():
            topic_content = f"""
            <h1>{topic}</h1>
            <p>This section covers the topic of {topic} in {event_name}.</p>
            
            <h2>Key Questions</h2>
            <ul>
            {"".join(f"<li>{q['text']}</li>" for q in topic_questions[:5])}
            </ul>
            
            <h2>Study Notes</h2>
            <p>Based on the questions in this topic, you should focus on the following concepts:</p>
            <ul>
            <li>Placeholder: Content would be generated by AI based on questions</li>
            </ul>
            """
            
            # Save topic content
            topic_blob = bucket.blob(f"binders/{binder_ref.id}/{topic}.html")
            topic_blob.upload_from_string(topic_content, content_type='text/html')
        
        return jsonify({
            "id": binder_ref.id,
            "message": "Study materials generated successfully"
        }), 201
    
    except Exception as e:
        logger.error(f"Error generating study materials: {str(e)}")
        return jsonify({"error": str(e)}), 500 