-- Create User Table
CREATE TABLE User (
    userId INT AUTO_INCREMENT PRIMARY KEY,
    firstName VARCHAR(255) NOT NULL,
    lastName VARCHAR(255) NOT NULL,
    userName VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Company Table
CREATE TABLE Company (
    companyId INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT
);

-- Create Profile Table
CREATE TABLE Profile (
    profileId INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL
);

-- Create Job Table
CREATE TABLE Job (
    jobId INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    requirements TEXT,
    companyId INT,
    FOREIGN KEY (companyId) REFERENCES Company(companyId) ON DELETE SET NULL
);

-- Create Quiz Table
CREATE TABLE Quiz (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profileId INT NOT NULL,
    jobId INT NOT NULL,
    questionIds JSON NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    userId INT NOT NULL,
    timer INT  NOT NULL,
    numberQuestions INT NOT NULL,
    FOREIGN KEY (profileId) REFERENCES Profile(profileId) ON DELETE SET NULL,
    FOREIGN KEY (jobId) REFERENCES Job(jobId) ON DELETE SET NULL,
    FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE SET NULL
);

-- Create Questions Table
CREATE TABLE Questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profileId INT,
    text TEXT NOT NULL,
    type VARCHAR(50),
    options JSON,
    answer JSON,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (profileId) REFERENCES Profile(profileId) ON DELETE SET NULL
);

-- Create Resume Table
CREATE TABLE Resume (
    resumeId INT AUTO_INCREMENT PRIMARY KEY,
    userId INT,
    jobId INT,
    resumeUrl VARCHAR(255),
    uploadedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE,
    FOREIGN KEY (jobId) REFERENCES Job(jobId) ON DELETE SET NULL
);

-- Create Application Table
CREATE TABLE Application (
    applicationId INT AUTO_INCREMENT PRIMARY KEY,
    userId INT,
    jobId INT,
    resumeId INT,
    status VARCHAR(100) DEFAULT 'Pending',
    submittedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE,
    FOREIGN KEY (jobId) REFERENCES Job(jobId) ON DELETE SET NULL,
    FOREIGN KEY (resumeId) REFERENCES Resume(resumeId) ON DELETE SET NULL
);

-- Create QuizHistory Table
CREATE TABLE QuizHistory (
    historyId INT AUTO_INCREMENT PRIMARY KEY,
    userId INT,
    quizId INT,
    score DECIMAL(5, 2),
    status VARCHAR(50),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    correctAnswers INT,
    totalQuestions INT,
    scorePercentage DECIMAL(5, 2),
    notAnsweredOrFalse INT,
    results JSON,
    FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE,
    FOREIGN KEY (quizId) REFERENCES Quiz(id) ON DELETE CASCADE
);
