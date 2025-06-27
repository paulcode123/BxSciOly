# Test Parsing Logic Upgrade

## Overview
The test parsing logic has been upgraded to use GPT-4o-mini instead of complex regex-based pattern matching for question extraction and topic classification.

## Changes Made

### 1. Updated OpenAI Integration
- **Old**: Used deprecated `import openai` with `openai.api_key` configuration
- **New**: Uses modern `from openai import OpenAI` with client-based approach
- **Requirement**: Updated `openai>=1.30.0` in requirements.txt

### 2. Simplified Question Extraction
- **Old**: Complex regex patterns and fallback mechanisms (~200 lines of code)
- **New**: Single GPT-4o-mini API call that handles both question segmentation and topic labeling
- **Benefits**: 
  - More accurate question boundaries
  - Better handling of multi-part questions
  - Automatic topic classification
  - Reduced code complexity

### 3. Streamlined Workflow
- **Old**: `extract_questions()` → `classify_question_topics()` → `create_knowledge_graph()`
- **New**: `extract_questions()` (with built-in topics) → `create_knowledge_graph()`
- **Result**: Faster processing and reduced API calls

### 4. Enhanced Topic Classification
- **Old**: Basic keyword matching with fallback to generic topics
- **New**: AI-powered topic identification specific to Science Olympiad events
- **Features**:
  - Event-specific topic suggestions
  - Multiple topics per question
  - Diagram/visual element detection

## API Usage

The new `extract_questions()` function uses the following GPT-4o-mini prompt structure:

```python
system_prompt = f"""You are an expert at analyzing Science Olympiad test documents for the event "{event_name}". 

Your task is to:
1. Identify and segment individual questions from the provided text
2. Extract each question's full text (including any sub-parts, multiple choice options, etc.)
3. Determine which page each question appears on
4. Assign relevant topic labels to each question

Return your response as a JSON array where each element is a question object with this structure:
{
    "number": <question_number>,
    "text": "<full_question_text>",
    "page": <page_number>,
    "topics": ["<topic1>", "<topic2>"],
    "has_diagram": <true/false>
}
```

## Configuration Required

Ensure your `api_keys.json` file contains the OpenAI API key:

```json
{
    "OpenAiAPIKey": "your-openai-api-key-here"
}
```

## Testing

To test the new parsing logic:

1. Upload a test PDF through the web interface
2. Select the appropriate Science Olympiad event
3. Use the "Parse Test" functionality
4. Review the extracted questions and topics in the parsed test viewer

## Backward Compatibility

- The `classify_question_topics()` function is maintained for compatibility but now just returns questions unchanged
- All existing API endpoints continue to work as expected
- Database schema remains the same

## Performance Improvements

- **Reduced Processing Time**: Single AI call vs multiple regex passes
- **Better Accuracy**: AI understanding vs pattern matching
- **Scalability**: Handles diverse question formats automatically
- **Maintainability**: Much simpler codebase to maintain and extend 