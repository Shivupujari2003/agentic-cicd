from fastapi import FastAPI, HTTPException, status, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import List, Optional
from datetime import datetime
import uvicorn
import logging
import os
from dotenv import load_dotenv

# Import AI email agent and webhook handler
from ai_email_agent import ai_email_agent
from github_webhook_handler import github_webhook_handler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Database Models
class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    __table_args__ = {'extend_existing': True}  # Allow table redefinition
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

class TaskCreate(SQLModel):
    title: str = Field(..., min_length=1, max_length=500, description="Task title (1-500 characters)")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Complete the project documentation"
            }
        }

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Updated task title")
    completed: Optional[bool] = Field(None, description="Task completion status")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Updated task title",
                "completed": True
            }
        }

class TaskResponse(SQLModel):
    id: int
    title: str
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime]

class HealthResponse(SQLModel):
    status: str
    timestamp: datetime
    version: str
    database_connected: bool

# Database setup - Neon PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is required")
    raise ValueError("DATABASE_URL environment variable is required")

logger.info(f"Connecting to database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")

# Configure engine for PostgreSQL
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

from contextlib import asynccontextmanager

# Database initialization function
def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# Lifespan handler for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Agentic CI/CD Task Manager API")
    create_db_and_tables()
    yield
    # Shutdown
    logger.info("Shutting down Agentic CI/CD Task Manager API")

def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session

# FastAPI app
app = FastAPI(
    title="Agentic CI/CD Task Manager API",
    description="Enterprise-grade Task Management API with AI-powered DevOps integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and CI/CD pipeline"""
    try:
        # Test database connection
        with Session(engine) as session:
            session.exec(select(Task)).first()
        db_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_connected = False
    
    return HealthResponse(
        status="healthy" if db_connected else "unhealthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database_connected=db_connected
    )

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🚀 Agentic CI/CD Task Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "description": "Enterprise-grade Task Management with AI-powered DevOps integration"
    }

# Task API Endpoints
@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
async def get_tasks(session: Session = Depends(get_session)):
    """Get all tasks with pagination support"""
    try:
        logger.info("Fetching all tasks")
        tasks = session.exec(select(Task)).all()
        logger.info(f"Retrieved {len(tasks)} tasks")
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching tasks"
        )

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    """Create a new task"""
    try:
        logger.info(f"Creating new task: {task.title}")
        
        # Validate input
        if not task.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot be empty"
            )
        
        db_task = Task(title=task.title.strip())
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        
        logger.info(f"Task created successfully with ID: {db_task.id}")
        return db_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating task"
        )

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(task_id: int, session: Session = Depends(get_session)):
    """Get a specific task by ID"""
    try:
        logger.info(f"Fetching task with ID: {task_id}")
        task = session.get(Task, task_id)
        if not task:
            logger.warning(f"Task with ID {task_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching task"
        )

@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(task_id: int, task: TaskUpdate, session: Session = Depends(get_session)):
    """Update an existing task"""
    try:
        logger.info(f"Updating task with ID: {task_id}")
        
        db_task = session.get(Task, task_id)
        if not db_task:
            logger.warning(f"Task with ID {task_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        # Update fields
        task_data = task.dict(exclude_unset=True)
        for key, value in task_data.items():
            setattr(db_task, key, value)
        
        db_task.updated_at = datetime.utcnow()
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        
        logger.info(f"Task {task_id} updated successfully")
        return db_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating task"
        )

@app.delete("/tasks/{task_id}", tags=["Tasks"])
async def delete_task(task_id: int, session: Session = Depends(get_session)):
    """Delete a task"""
    try:
        logger.info(f"Deleting task with ID: {task_id}")
        
        task = session.get(Task, task_id)
        if not task:
            logger.warning(f"Task with ID {task_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        session.delete(task)
        session.commit()
        
        logger.info(f"Task {task_id} deleted successfully")
        return {"message": f"Task {task_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting task"
        )

# Additional endpoints for CI/CD integration
@app.get("/tasks/stats", tags=["Analytics"])
async def get_task_stats(session: Session = Depends(get_session)):
    """Get task statistics for monitoring and dashboards"""
    try:
        tasks = session.exec(select(Task)).all()
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.completed)
        pending_tasks = total_tasks - completed_tasks
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
        }
    except Exception as e:
        logger.error(f"Error fetching task stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching statistics"
        )

# AI Email Agent Endpoints
@app.post("/webhooks/github", tags=["Webhooks"])
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    GitHub webhook endpoint for PR notifications
    Configure this URL in your GitHub repository webhook settings
    """
    try:
        result = await github_webhook_handler.handle_webhook(request, background_tasks)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook handling error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing webhook"
        )

@app.post("/ai-email/test", tags=["AI Email Agent"])
async def test_ai_email_service():
    """Test the AI email service with sample data"""
    try:
        logger.info("Testing AI email service")
        result = ai_email_agent.test_email_service()
        return result
    except Exception as e:
        logger.error(f"Error testing AI email service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while testing email service"
        )

@app.post("/ai-email/send-pr-notification", tags=["AI Email Agent"])
async def send_pr_notification(pr_data: dict):
    """
    Manually trigger a PR notification email
    Useful for testing or manual notifications
    """
    try:
        logger.info(f"Manual PR notification requested for: {pr_data}")
        success = ai_email_agent.process_pr_notification(pr_data)
        
        if success:
            return {
                "status": "success",
                "message": "PR notification email sent successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send PR notification email"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending manual PR notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while sending notification"
        )

@app.get("/ai-email/status", tags=["AI Email Agent"])
async def get_ai_email_status():
    """Get the status and configuration of the AI email service"""
    try:
        # Check if all required environment variables are set
        config_status = {
            "azure_openai_configured": bool(os.getenv("AZURE_OPENAI_API_KEY")),
            "email_configured": bool(os.getenv("EMAIL_USERNAME") and os.getenv("EMAIL_PASSWORD")),
            "owner_email_configured": bool(os.getenv("OWNER_EMAIL")),
            "webhook_secret_configured": bool(os.getenv("GITHUB_WEBHOOK_SECRET")),
            "project_name": os.getenv("PROJECT_NAME", "Agentic CI/CD Task Manager"),
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "azure_endpoint": os.getenv("ENDPOINT_URL", "Not configured"),
            "deployment_name": os.getenv("DEPLOYMENT_NAME", "gpt-4o")
        }
        
        return {
            "status": "operational" if all([
                config_status["azure_openai_configured"],
                config_status["email_configured"],
                config_status["owner_email_configured"]
            ]) else "configuration_incomplete",
            "configuration": config_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking AI email status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while checking status"
        )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.utcnow().isoformat()}
    )

# Main execution
if __name__ == "__main__":
    logger.info("Starting Agentic CI/CD Task Manager API server")
    uvicorn.run(
        "task_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
