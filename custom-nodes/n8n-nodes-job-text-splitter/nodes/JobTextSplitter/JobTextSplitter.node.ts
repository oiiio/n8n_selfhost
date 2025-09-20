import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	NodeOperationError,
} from 'n8n-workflow';

export class JobTextSplitter implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'Job Text Splitter',
		name: 'jobTextSplitter',
		icon: 'fa:cut',
		group: ['transform'],
		version: 1,
		description: 'Split job data into optimized chunks for vector embeddings and search',
		defaults: {
			name: 'Job Text Splitter',
		},
		inputs: ['main'],
		outputs: ['main'],
		properties: [
			{
				displayName: 'Splitting Strategy',
				name: 'strategy',
				type: 'options',
				options: [
					{
						name: 'By Job Section',
						value: 'bySection',
						description: 'Split each job into semantic sections (title, description, qualifications, etc.)',
					},
					{
						name: 'By Character Count',
						value: 'byCharacter',
						description: 'Split job content into chunks of specified character count',
					},
					{
						name: 'By Token Estimate',
						value: 'byToken',
						description: 'Split based on estimated token count for embeddings',
					},
					{
						name: 'Hybrid',
						value: 'hybrid',
						description: 'Combine section-based splitting with character limits',
					},
				],
				default: 'hybrid',
				description: 'Choose how to split the job data for optimal embedding',
			},
			{
				displayName: 'Max Chunk Size',
				name: 'maxChunkSize',
				type: 'number',
				default: 1000,
				description: 'Maximum characters per chunk (for character/token strategies)',
				displayOptions: {
					show: {
						strategy: ['byCharacter', 'byToken', 'hybrid'],
					},
				},
			},
			{
				displayName: 'Chunk Overlap',
				name: 'chunkOverlap',
				type: 'number',
				default: 200,
				description: 'Number of characters to overlap between chunks',
				displayOptions: {
					show: {
						strategy: ['byCharacter', 'byToken', 'hybrid'],
					},
				},
			},
			{
				displayName: 'Include Metadata',
				name: 'includeMetadata',
				type: 'boolean',
				default: true,
				description: 'Include job metadata (location, ID, etc.) in each chunk',
			},
			{
				displayName: 'Metadata Fields',
				name: 'metadataFields',
				type: 'multiOptions',
				options: [
					{ name: 'Job ID', value: 'job_id' },
					{ name: 'Title', value: 'title' },
					{ name: 'Location', value: 'location' },
					{ name: 'Posted Date', value: 'posted_date' },
					{ name: 'Job Type', value: 'job_type' },
					{ name: 'URL', value: 'url' },
					{ name: 'Security Clearance', value: 'security_clearance' },
					{ name: 'Experience Years', value: 'experience_years' },
					{ name: 'Salary Range', value: 'salary_range' },
				],
				default: ['job_id', 'title', 'location', 'job_type'],
				description: 'Which metadata fields to include with each chunk',
				displayOptions: {
					show: {
						includeMetadata: [true],
					},
				},
			},
			{
				displayName: 'Preserve Context',
				name: 'preserveContext',
				type: 'boolean',
				default: true,
				description: 'Add contextual information to each chunk for better embeddings',
			},
			{
				displayName: 'Add Chunk Index',
				name: 'addChunkIndex',
				type: 'boolean',
				default: true,
				description: 'Add chunk index and total count to metadata',
			},
		],
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[]> {
		const items = this.getInputData();
		const results: INodeExecutionData[] = [];

		const strategy = this.getNodeParameter('strategy', 0) as string;
		const maxChunkSize = this.getNodeParameter('maxChunkSize', 0) as number;
		const chunkOverlap = this.getNodeParameter('chunkOverlap', 0) as number;
		const includeMetadata = this.getNodeParameter('includeMetadata', 0) as boolean;
		const metadataFields = this.getNodeParameter('metadataFields', 0) as string[];
		const preserveContext = this.getNodeParameter('preserveContext', 0) as boolean;
		const addChunkIndex = this.getNodeParameter('addChunkIndex', 0) as boolean;

		for (let itemIndex = 0; itemIndex < items.length; itemIndex++) {
			try {
				const item = items[itemIndex];
				const jobData = item.json;

				// Handle different input formats (single job or array of jobs)
				const jobs = Array.isArray(jobData) ? jobData : 
					         jobData.jobs ? jobData.jobs : [jobData];

				for (const job of jobs) {
					const chunks = this.splitJobData(
						job,
						strategy,
						maxChunkSize,
						chunkOverlap,
						includeMetadata,
						metadataFields,
						preserveContext
					);

					// Add chunk index if requested
					if (addChunkIndex) {
						chunks.forEach((chunk: any, index: number) => {
							chunk.metadata = {
								...chunk.metadata,
								chunk_index: index + 1,
								total_chunks: chunks.length,
							};
						});
					}

					// Add each chunk as a separate item
					for (const chunk of chunks) {
						results.push({
							json: {
								content: chunk.content,
								metadata: chunk.metadata,
								source: 'job_text_splitter',
								original_job_id: job.job_id || job.id,
							},
						});
					}
				}
			} catch (error: any) {
				throw new NodeOperationError(
					this.getNode(),
					`Error processing item ${itemIndex}: ${error.message}`,
					{ itemIndex }
				);
			}
		}

		return results;
	}

	private splitJobData(
		job: any,
		strategy: string,
		maxChunkSize: number,
		chunkOverlap: number,
		includeMetadata: boolean,
		metadataFields: string[],
		preserveContext: boolean
	): Array<{ content: string; metadata: any }> {
		// Extract metadata if requested
		const metadata = includeMetadata ? this.extractMetadata(job, metadataFields) : {};

		switch (strategy) {
			case 'bySection':
				return this.splitBySection(job, metadata, preserveContext);
			case 'byCharacter':
				return this.splitByCharacter(job, maxChunkSize, chunkOverlap, metadata, preserveContext);
			case 'byToken':
				return this.splitByToken(job, maxChunkSize, chunkOverlap, metadata, preserveContext);
			case 'hybrid':
				return this.splitHybrid(job, maxChunkSize, chunkOverlap, metadata, preserveContext);
			default:
				throw new Error(`Unknown splitting strategy: ${strategy}`);
		}
	}

	private extractMetadata(job: any, fields: string[]): any {
		const metadata: any = {};
		
		for (const field of fields) {
			if (job[field] !== undefined && job[field] !== null && job[field] !== '') {
				metadata[field] = job[field];
			}
		}
		
		return metadata;
	}

	private splitBySection(job: any, metadata: any, preserveContext: boolean): Array<{ content: string; metadata: any }> {
		const chunks: Array<{ content: string; metadata: any }> = [];
		const contextPrefix = preserveContext ? this.buildContextPrefix(job) : '';

		// Define important job sections and their priorities
		const sections = [
			{ key: 'title', label: 'Job Title', priority: 1 },
			{ key: 'description', label: 'Job Description', priority: 2 },
			{ key: 'qualifications', label: 'Qualifications', priority: 3 },
			{ key: 'responsibilities', label: 'Responsibilities', priority: 3 },
			{ key: 'requirements', label: 'Requirements', priority: 3 },
			{ key: 'benefits', label: 'Benefits', priority: 4 },
			{ key: 'experience_level', label: 'Experience Level', priority: 2 },
			{ key: 'department', label: 'Department', priority: 4 },
		];

		// Create chunks for each section that exists
		for (const section of sections) {
			const content = job[section.key];
			if (content && typeof content === 'string' && content.trim().length > 0) {
				const chunkContent = contextPrefix + `${section.label}: ${content.trim()}`;
				
				chunks.push({
					content: chunkContent,
					metadata: {
						...metadata,
						section: section.key,
						section_label: section.label,
						section_priority: section.priority,
					},
				});
			}
		}

		// If no sections found, create a single chunk with available content
		if (chunks.length === 0) {
			const fallbackContent = this.buildFallbackContent(job);
			if (fallbackContent) {
				chunks.push({
					content: contextPrefix + fallbackContent,
					metadata: {
						...metadata,
						section: 'combined',
						section_label: 'Combined Content',
					},
				});
			}
		}

		return chunks;
	}

	private splitByCharacter(job: any, maxSize: number, overlap: number, metadata: any, preserveContext: boolean): Array<{ content: string; metadata: any }> {
		const fullContent = this.buildFullContent(job, preserveContext);
		return this.chunkText(fullContent, maxSize, overlap, metadata);
	}

	private splitByToken(job: any, maxTokens: number, overlap: number, metadata: any, preserveContext: boolean): Array<{ content: string; metadata: any }> {
		// Rough token estimation: ~4 characters per token for English text
		const estimatedMaxChars = maxTokens * 4;
		const estimatedOverlapChars = overlap * 4;
		
		const fullContent = this.buildFullContent(job, preserveContext);
		return this.chunkText(fullContent, estimatedMaxChars, estimatedOverlapChars, {
			...metadata,
			estimated_tokens: Math.ceil(fullContent.length / 4),
		});
	}

	private splitHybrid(job: any, maxSize: number, overlap: number, metadata: any, preserveContext: boolean): Array<{ content: string; metadata: any }> {
		// First, try section-based splitting
		const sectionChunks = this.splitBySection(job, metadata, preserveContext);
		
		// Then, split any oversized chunks further
		const finalChunks: Array<{ content: string; metadata: any }> = [];
		
		for (const chunk of sectionChunks) {
			if (chunk.content.length <= maxSize) {
				finalChunks.push(chunk);
			} else {
				// Split oversized chunks
				const subChunks = this.chunkText(chunk.content, maxSize, overlap, chunk.metadata);
				finalChunks.push(...subChunks);
			}
		}
		
		return finalChunks;
	}

	private chunkText(text: string, maxSize: number, overlap: number, metadata: any): Array<{ content: string; metadata: any }> {
		const chunks: Array<{ content: string; metadata: any }> = [];
		
		if (text.length <= maxSize) {
			return [{ content: text, metadata }];
		}
		
		let start = 0;
		let chunkIndex = 0;
		
		while (start < text.length) {
			let end = start + maxSize;
			
			// Try to break at a sentence or paragraph boundary
			if (end < text.length) {
				const sentenceEnd = text.lastIndexOf('.', end);
				const paragraphEnd = text.lastIndexOf('\n\n', end);
				const breakPoint = Math.max(sentenceEnd, paragraphEnd);
				
				if (breakPoint > start + maxSize / 2) {
					end = breakPoint + 1;
				}
			}
			
			const chunkText = text.slice(start, end).trim();
			if (chunkText.length > 0) {
				chunks.push({
					content: chunkText,
					metadata: {
						...metadata,
						chunk_size: chunkText.length,
						sub_chunk_index: chunkIndex,
					},
				});
			}
			
			start = Math.max(start + 1, end - overlap);
			chunkIndex++;
		}
		
		return chunks;
	}

	private buildContextPrefix(job: any): string {
		const title = job.title || 'Job Position';
		const location = job.location || '';
		const company = 'Booz Allen Hamilton';
		
		return `Job posting for ${title}${location ? ` in ${location}` : ''} at ${company}. `;
	}

	private buildFullContent(job: any, includeContext: boolean): string {
		const parts: string[] = [];
		
		if (includeContext) {
			parts.push(this.buildContextPrefix(job));
		}
		
		// Add content in order of importance
		const contentFields = [
			'title', 'description', 'qualifications', 'responsibilities', 
			'requirements', 'experience_level', 'benefits', 'department'
		];
		
		for (const field of contentFields) {
			const content = job[field];
			if (content && typeof content === 'string' && content.trim().length > 0) {
				parts.push(`${field.replace('_', ' ').toUpperCase()}: ${content.trim()}`);
			}
		}
		
		// If no structured content, try to build from any available text
		if (parts.length <= (includeContext ? 1 : 0)) {
			const fallback = this.buildFallbackContent(job);
			if (fallback) {
				parts.push(fallback);
			}
		}
		
		return parts.join('\n\n');
	}

	private buildFallbackContent(job: any): string {
		const parts: string[] = [];
		
		// Try to extract any text content from the job object
		for (const [key, value] of Object.entries(job)) {
			if (typeof value === 'string' && value.trim().length > 10) {
				// Skip metadata-only fields
				if (!['job_id', 'url', 'posted_date', 'external_path'].includes(key)) {
					parts.push(`${key.replace('_', ' ')}: ${value.trim()}`);
				}
			}
		}
		
		return parts.join('\n');
	}
}