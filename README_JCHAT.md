# jChat: jewelry product assistant

This POC uses AWS Bedrock Converse for generation, local PDF extraction, an in-memory lexical vector adapter, chat memory, and Streamlit. The application core is separated from adapters so the retriever can later be replaced by Amazon OpenSearch Serverless or Milvus without changing the UI or use cases.

The UI starts in **Mock** mode, so it does not need AWS credentials. Switch the sidebar provider to **AWS** after configuring your AWS profile.

## Run

```powershell
cd D:\CodeBase\GenAI\genai-hackathon-main
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-jchat.txt
$env:AWS_PROFILE = "your-profile"
$env:AWS_REGION = "us-west-2"
streamlit run jchat/streamlit_app.py
```

For a credential-free demo, omit the AWS variables and leave **Chat provider: Mock** selected. For Bedrock, select **AWS**, choose the model ID, and ensure the IAM identity can call `bedrock:Converse` for that model.

The AWS identity needs Bedrock model invocation permission for the configured model. The POC does not store AWS keys in source files. It indexes uploaded PDFs in memory for the running process; restarting Streamlit clears the index.

## Git handoff

This reference folder did not contain a Git repository or remote when the POC was created. To publish it, initialize a repository and add your remote:

```powershell
git init
git add .
git commit -m "Build jChat Bedrock RAG POC"
git remote add origin <your-repository-url>
git push -u origin main
```

## Architecture

- `domain.py`: entities with no AWS or Streamlit imports.
- `ports.py`: model, retriever, and memory boundaries.
- `application.py`: ingestion and conversational RAG use cases.
- `bedrock.py`: AWS Bedrock adapter using `converse`.
- `adapters.py`: in-memory retriever and chat memory; replace the retriever with OpenSearch Serverless or Milvus for production.
- `documents.py`: PDF extraction adapter.
- `streamlit_app.py`: thin POC UI.

