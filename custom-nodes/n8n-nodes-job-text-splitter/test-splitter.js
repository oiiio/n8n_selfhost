/**
 * Test file to demonstrate the Job Text Splitter functionality
 * Run with: node test-splitter.js
 */

// Mock job data similar to what the BAH scraper produces
const sampleJobData = {
  jobs: [
    {
      job_id: "R0123456",
      title: "Senior Software Engineer",
      location: "McLean, VA",
      posted_date: "2025-01-15",
      job_type: "Full-time",
      url: "https://bah.wd1.myworkdayjobs.com/job/123456",
      description: `We are seeking a highly skilled Senior Software Engineer to join our dynamic team. You will be responsible for designing, developing, and maintaining complex software systems that support critical mission objectives. This role requires expertise in modern software development practices, cloud technologies, and system architecture.

Key responsibilities include leading technical design discussions, mentoring junior developers, and ensuring code quality through comprehensive testing and code reviews. You will work closely with cross-functional teams including product managers, designers, and other engineers to deliver high-quality software solutions.

The ideal candidate will have experience with distributed systems, microservices architecture, and cloud platforms such as AWS or Azure. Strong communication skills and the ability to work in a fast-paced, collaborative environment are essential.`,
      
      qualifications: `• Bachelor's degree in Computer Science, Engineering, or related field
• 5+ years of experience in software development
• Proficiency in Java, Python, or C# programming languages
• Experience with cloud platforms (AWS, Azure, GCP)
• Strong understanding of software design patterns and principles
• Experience with containerization technologies (Docker, Kubernetes)
• Knowledge of CI/CD pipelines and DevOps practices
• Excellent problem-solving and analytical skills`,

      responsibilities: `• Design and implement scalable software solutions
• Lead technical architecture discussions and decisions
• Mentor and guide junior team members
• Conduct code reviews and ensure code quality standards
• Collaborate with cross-functional teams on product requirements
• Participate in agile development processes
• Troubleshoot and resolve complex technical issues
• Stay current with emerging technologies and industry best practices`,

      security_clearance: "TS/SCI with polygraph",
      experience_years: "5",
      salary_range: "$120,000 - $160,000 annually"
    },
    {
      job_id: "R0789012",
      title: "Data Scientist",
      location: "Remote",
      posted_date: "2025-01-10",
      job_type: "Contract",
      url: "https://bah.wd1.myworkdayjobs.com/job/789012",
      description: "Join our data science team to develop cutting-edge machine learning models and analytics solutions. This position focuses on extracting insights from large datasets to drive business decisions and improve operational efficiency.",
      
      qualifications: `• Master's degree in Data Science, Statistics, or related field
• 3+ years of experience in data science or machine learning
• Proficiency in Python and R programming languages
• Experience with ML frameworks (TensorFlow, PyTorch, scikit-learn)
• Strong statistical analysis and modeling skills`,

      security_clearance: "Secret clearance required",
      experience_years: "3"
    }
  ]
};

// Simulate the node's splitting logic
function simulateTextSplitting() {
  console.log("=== Job Text Splitter Simulation ===\n");
  
  const jobs = sampleJobData.jobs;
  let totalChunks = 0;
  
  for (const job of jobs) {
    console.log(`Processing Job: ${job.title} (${job.job_id})`);
    console.log(`Location: ${job.location}`);
    console.log("---");
    
    // Simulate "By Section" strategy
    const sections = [
      { key: 'title', label: 'Job Title', content: job.title },
      { key: 'description', label: 'Job Description', content: job.description },
      { key: 'qualifications', label: 'Qualifications', content: job.qualifications },
      { key: 'responsibilities', label: 'Responsibilities', content: job.responsibilities }
    ];
    
    let chunkIndex = 1;
    const jobChunks = [];
    
    for (const section of sections) {
      if (section.content && section.content.trim().length > 0) {
        const contextPrefix = `Job posting for ${job.title} in ${job.location} at Booz Allen Hamilton. `;
        const chunkContent = contextPrefix + `${section.label}: ${section.content.trim()}`;
        
        const chunk = {
          content: chunkContent,
          metadata: {
            job_id: job.job_id,
            title: job.title,
            location: job.location,
            job_type: job.job_type,
            section: section.key,
            section_label: section.label,
            security_clearance: job.security_clearance,
            experience_years: job.experience_years,
            chunk_index: chunkIndex,
            chunk_size: chunkContent.length
          },
          source: 'job_text_splitter',
          original_job_id: job.job_id
        };
        
        jobChunks.push(chunk);
        chunkIndex++;
      }
    }
    
    // Add total_chunks to all chunks
    jobChunks.forEach(chunk => {
      chunk.metadata.total_chunks = jobChunks.length;
    });
    
    console.log(`Generated ${jobChunks.length} chunks:`);
    jobChunks.forEach((chunk, i) => {
      console.log(`  ${i + 1}. ${chunk.metadata.section_label} (${chunk.metadata.chunk_size} chars)`);
      if (i === 0) {
        console.log(`     Preview: "${chunk.content.substring(0, 100)}..."`);
        console.log(`     Metadata:`, JSON.stringify(chunk.metadata, null, 2));
      }
    });
    
    totalChunks += jobChunks.length;
    console.log("\n");
  }
  
  console.log(`Total chunks generated: ${totalChunks}`);
  
  // Show example of how this would work with embeddings
  console.log("\n=== Example Vector Database Integration ===");
  console.log("1. Each chunk would be sent to Gemini Embedding 001");
  console.log("2. The resulting vectors would be stored in Pinecone with metadata");
  console.log("3. Search queries would find relevant chunks based on semantic similarity");
  console.log("4. Metadata allows filtering by location, clearance level, experience, etc.");
  
  console.log("\n=== Example Search Queries ===");
  console.log("• 'Python machine learning experience' → Would find Data Scientist chunks");
  console.log("• 'software architecture design' → Would find Senior Software Engineer chunks");
  console.log("• Filter: location='Remote' → Would return only remote job chunks");
  console.log("• Filter: security_clearance contains 'TS/SCI' → High clearance jobs only");
}

// Run the simulation
simulateTextSplitting();