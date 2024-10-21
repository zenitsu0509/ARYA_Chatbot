class AryaChatbot:
    def __init__(self, pinecone_api_key: str, pinecone_env: str, huggingface_api: str):
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_env = pinecone_env
        self.huggingface_api = huggingface_api
        self.vector_store = None
        self.llm = None
        self.qa_chain = None
        
    def _setup_pinecone(self, index_name: str = "arya-index-o") -> PineconeVectorStore:
        """Initialize Pinecone with optimized settings."""
        try:
            pc = Pinecone(api_key=self.pinecone_api_key, environment=self.pinecone_env)
            index = pc.Index(index_name)
            
            # Use smaller, faster embedding model
            embeddings = HuggingFaceEmbeddings(
                model_name="intfloat/multilingual-e5-small",  # Changed to smaller model
                encode_kwargs={
                    'normalize_embeddings': True,
                    'batch_size': 8  # Added batch size for efficiency
                }
            )
            
            return PineconeVectorStore(
                index=index,
                embedding=embeddings,
                namespace="ns1",
                top_k=3  # Limit number of results
            )
        except PineconeException as e:
            raise Exception(f"Failed to initialize Pinecone: {str(e)}")

    def _setup_llm(self) -> HuggingFaceEndpoint:
        """Initialize the language model with optimized parameters."""
        repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        endpoint_url = f"https://api-inference.huggingface.co/models/{repo_id}"
        
        return HuggingFaceEndpoint(
            endpoint_url=endpoint_url,
            huggingfacehub_api_token=self.huggingface_api,
            max_length=256,  # Reduced from 512
            temperature=0.7,
            top_k=30,  # Reduced from 50
            num_return_sequences=1,
            task="text2text-generation",
            model_kwargs={
                "max_new_tokens": 150,  # Limit response length
                "do_sample": True,
                "top_p": 0.9
            }
        )

    def get_response(self, question: str) -> str:
        """Get optimized response for a given question."""
        try:
            if not self.qa_chain:
                raise Exception("Chatbot not initialized")
            
            # Limit question length
            question = question[:200] if len(question) > 200 else question
            
            response = self.qa_chain.invoke(question)
            return response['result'][:500]  # Limit response length
        except Exception as e:
            raise Exception(f"Error: {str(e)}")