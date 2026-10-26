import boto3
from config import KB_ID, MODEL_ID

region_name = "us-west-2"  

# Initialize the Bedrock client
bedrock_agent_runtime_client = boto3.client("bedrock-agent-runtime", region_name=region_name)

def ask_bedrock_llm_with_knowledge_base(query: str, model_arn: str, kb_id: str) -> dict:
    try:
        response = bedrock_agent_runtime_client.retrieve_and_generate(
            input={
                'text': query
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': model_arn,
                    'generationConfiguration': {
                        'guardrailConfiguration': {
                            'guardrailId': 'anu7un828i2p',
                            'guardrailVersion': '5' 
                        },
                        'inferenceConfig': {
                            'textInferenceConfig': {
                                'maxTokens': 512,
                                'temperature': 0.1,
                                'topP': 0.9
                            }
                        },
                        'promptTemplate': {
                            'textPromptTemplate': (
                                'Given the following search results:\n\n$search_results$\n\n'
                                'Answer the following question based on the most relevant and meaningful information from the search results. '
                                'Ignore any redundant or irrelevant details: {text}'
                            )
                        }
                    },
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': 10,
                            'overrideSearchType': 'SEMANTIC'  # Set to SEMANTIC or HYBRID
                        }
                    }
                }
            },
        )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

def handle_guardrail_block() -> str:
    return "I'm sorry, but I can't provide an answer to that question at the moment due to system constraints. If you have any other questions or need further assistance, please feel free to ask!"

def handle_no_matching_context() -> str:
    return "It seems that the search results do not contain relevant information to answer your question. If you have any other questions or need further assistance, please let me know!"

def get_text_response(query: str) -> str:
    # Predefined responses for specific queries
    greetings = ["hi", "hello", "hey"]
    introductions = ["who are you", "what are you", "what's your name", "how are you "]
    
    query_lower = query.strip().lower()
    
    if query_lower in greetings:
        return "Hello! How can I assist you today?"
    elif query_lower in introductions:
        return "I am a bot assisting with aerospace inquiries. How can I help you today?"

    # If query is not a predefined response, call the Bedrock API
    model_arn = f'arn:aws:bedrock:{region_name}::foundation-model/{MODEL_ID}'
    
    response = ask_bedrock_llm_with_knowledge_base(query, model_arn, KB_ID)
    
    if not response:
        return handle_no_matching_context()
    
    # Check for specific indicators of guardrail blocks
    response_text = response.get('output', {}).get('text', '')
    
    if "guardrail" in response_text.lower():
        return handle_guardrail_block()
    
    if not response_text.strip():
        return handle_no_matching_context()

    return response_text


