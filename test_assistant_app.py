import pytest
from unittest.mock import patch, MagicMock
from assistant_bot import get_text_response, handle_guardrail_block, handle_no_matching_context


@patch('boto3.client')
def test_get_text_response_guardrail_block(mock_boto_client):
    print("Running test_get_text_response_guardrail_block")
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.retrieve_and_generate.return_value = {
        'output': {
            'text': "Sorry, the model cannot answer this question due to guardrail constraints."
        }
    }
    response = get_text_response("kill?")
    assert response == handle_guardrail_block()


