// Simple test to debug the node behavior
const testLambdaResponse = {
  "jobs": [
    {
      "job_id": "test123",
      "title": "Software Engineer",
      "location": "McLean, VA",
      "description": "We are looking for a software engineer...",
      "qualifications": "Bachelor's degree in Computer Science...",
      "responsibilities": "Design and develop software applications..."
    }
  ]
};

// Simulate what our node should do
function createJobChunks(job) {
    const chunks = [];
    const contextPrefix = `Job posting for ${job.title || 'Position'} at Booz Allen Hamilton. `;
    
    const sections = [
        { key: 'title', label: 'Job Title' },
        { key: 'description', label: 'Description' },
        { key: 'qualifications', label: 'Qualifications' },
        { key: 'responsibilities', label: 'Responsibilities' },
    ];
    
    for (const section of sections) {
        if (job[section.key] && typeof job[section.key] === 'string') {
            const content = contextPrefix + `${section.label}: ${job[section.key]}`;
            chunks.push({
                content,
                metadata: {
                    job_id: job.job_id,
                    title: job.title,
                    location: job.location,
                    section: section.key,
                    section_label: section.label,
                    chunk_size: content.length,
                }
            });
        }
    }
    
    return chunks;
}

// Test the logic
console.log('Testing with Lambda response:', JSON.stringify(testLambdaResponse, null, 2));

let jobs;
if (Array.isArray(testLambdaResponse)) {
    jobs = testLambdaResponse;
} else if (testLambdaResponse.jobs && Array.isArray(testLambdaResponse.jobs)) {
    jobs = testLambdaResponse.jobs;
} else {
    jobs = [testLambdaResponse];
}

console.log('Jobs array:', jobs.length, 'jobs found');

const results = [];
for (const job of jobs) {
    const chunks = createJobChunks(job);
    console.log(`Job ${job.job_id} produced ${chunks.length} chunks`);
    
    for (const chunk of chunks) {
        results.push({
            json: {
                content: chunk.content,
                metadata: chunk.metadata,
                source: 'job_text_splitter',
                original_job_id: job.job_id || job.id || 'unknown',
            },
        });
    }
}

console.log('Total results:', results.length);
console.log('First result:', JSON.stringify(results[0], null, 2));