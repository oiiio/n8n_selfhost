# n8n-nodes-job-text-splitter

A custom n8n node for intelligently splitting job data into optimized chunks for vector embeddings and search. Perfect for processing job postings from scrapers like the BAH job scraper and preparing them for vector databases like Pinecone with Gemini embeddings.

## Features

- **Multiple Splitting Strategies**: Choose from section-based, character-based, token-based, or hybrid splitting
- **Smart Context Preservation**: Maintains job context in each chunk for better embeddings
- **Metadata Extraction**: Includes relevant job metadata with each chunk
- **Vector Database Optimized**: Designed specifically for embeddings and vector search
- **Flexible Configuration**: Customizable chunk sizes, overlap, and metadata fields

## Installation

### Method 1: Manual Installation (Recommended for Development)

1. Navigate to your n8n custom nodes directory:
```bash
cd ~/.n8n/custom/
```

2. Clone or copy this node:
```bash
cp -r /path/to/n8n-nodes-job-text-splitter ./
```

3. Install dependencies:
```bash
cd n8n-nodes-job-text-splitter
npm install
```

4. Build the node:
```bash
npm run build
```

5. Restart n8n

### Method 2: Direct Installation in n8n Docker

If using n8n in Docker, mount this directory as a volume and install it inside the container.

## Usage

### Input Data Format

The node accepts job data in several formats:
- Single job object
- Array of job objects  
- Response object with `jobs` array (like from the BAH job scraper)

### Splitting Strategies

#### 1. By Section (Recommended)
Splits jobs into semantic sections:
- Job Title
- Job Description  
- Qualifications
- Responsibilities
- Requirements
- Benefits
- Experience Level
- Department

Each section becomes a separate chunk with preserved metadata.

#### 2. By Character Count
Splits job content into chunks of specified character length with configurable overlap.

#### 3. By Token Estimate
Splits based on estimated token count (useful for embedding models with token limits).

#### 4. Hybrid (Best for Most Cases)
Combines section-based splitting with character limits - creates sections but further splits oversized sections.

### Configuration Options

- **Splitting Strategy**: Choose your preferred splitting method
- **Max Chunk Size**: Maximum characters per chunk (for character/token/hybrid strategies)
- **Chunk Overlap**: Characters to overlap between chunks for better context
- **Include Metadata**: Whether to include job metadata with each chunk
- **Metadata Fields**: Which job fields to include as metadata
- **Preserve Context**: Add contextual information to each chunk
- **Add Chunk Index**: Include chunk numbering in metadata

### Output Format

Each chunk is output as a separate item with:

```json
{
  "content": "Job Title: Software Engineer\\n\\nDetailed job description...",
  "metadata": {
    "job_id": "R0123456",
    "title": "Software Engineer",
    "location": "McLean, VA",
    "job_type": "Full-time",
    "section": "description",
    "section_label": "Job Description",
    "chunk_index": 1,
    "total_chunks": 3
  },
  "source": "job_text_splitter",
  "original_job_id": "R0123456"
}
```

## Use Cases

### Vector Database Storage
Perfect for storing job data in vector databases like Pinecone:
1. Split jobs with this node
2. Generate embeddings using Gemini Embedding 001
3. Store in Pinecone with metadata for filtering

### Semantic Search
Enable powerful job search capabilities:
- Search by job requirements
- Find jobs by skills mentioned
- Location-based filtering through metadata

### RAG Applications
Build AI assistants that can answer questions about job opportunities using the chunked and embedded job data.

## Example Workflow

1. **BAH Job Scraper** → Get job data
2. **Job Text Splitter** → Split into optimized chunks  
3. **Google Gemini Embedding** → Generate embeddings
4. **Pinecone** → Store vectors with metadata
5. **Query Interface** → Semantic job search

## Advanced Configuration

### For Large Jobs
- Use "Hybrid" strategy with 800-1000 character chunks
- Set 100-200 character overlap
- Include key metadata fields: job_id, title, location, job_type

### For Embedding Models
- Token-based strategy for models with strict token limits
- Character-based for consistent chunk sizes
- Always preserve context for better semantic understanding

### For Search Applications  
- Include comprehensive metadata for filtering
- Use section-based splitting to maintain semantic boundaries
- Add chunk indices for result reconstruction

## Troubleshooting

### Node Not Appearing
- Ensure n8n is restarted after installation
- Check that the node is built correctly (`npm run build`)
- Verify file permissions

### Memory Issues
- Reduce max chunk size for large datasets
- Process jobs in smaller batches
- Consider using character-based splitting for very large descriptions

### Poor Embedding Quality
- Enable context preservation
- Use hybrid or section-based splitting
- Include relevant metadata fields

## Development

### Building
```bash
npm run build
```

### Testing
```bash
npm test
```

### Linting
```bash
npm run lint
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.