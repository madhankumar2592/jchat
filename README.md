


# AIR LEGION

## Overview

AIR LEGION is a sophisticated application designed to leverage Retrieval-Augmented Generation (RAG) using AWS Bedrock. It utilizes the `anthropic.claude-3-haiku-20240307-v1:0` foundation model for both knowledge retrieval and generative tasks. The system integrates a knowledge base hosted in Amazon OpenSearch Service (AOSS), specifically tailored with airline domain data to provide accurate and contextually relevant responses.

## Features

- **Retrieval-Augmented Generation (RAG):** Enhances the generation of responses by retrieving pertinent information from a structured knowledge base.
- **Knowledge Base Integration:** Utilizes Amazon OpenSearch Service (AOSS) to manage and query a comprehensive airline domain knowledge base.
- **Foundation Models:** Employs `anthropic.claude-3-haiku-20240307-v1:0` for both retrieving and generating responses, ensuring consistency and accuracy.

## Architecture

1. **AWS Bedrock:** The core service enabling Retrieval-Augmented Generation (RAG) with the `RetrieveAndGenerate` capability.
2. **Amazon OpenSearch Service (AOSS):** Hosts the knowledge base enriched with airline domain data.
3. **Foundation Models:** `anthropic.claude-3-haiku-20240307-v1:0` is used for generating responses based on retrieved data from AOSS.

## Usage

To interact with AIR LEGION, simply query the system with your airline-related questions. The system retrieves relevant information from the knowledge base and generates accurate responses using the integrated foundation model.

## Developed by Team 26
Shalini , Cijo  , Madhan
