# Azure Cosmos DB Setup Guide for ByteMeCarbon

## Overview

This guide explains how to set up Azure Cosmos DB for ByteMeCarbon to store optimization results and maintain user history. This solves multi-user collision issues and enables data persistence.

---

## Part 1: Create Azure Cosmos DB Account

### Step 1.1: Create Azure Account
1. Go to https://azure.microsoft.com/en-us/free/
2. Click "Start Free"
3. Sign up with Microsoft account or email
4. Verify phone number and credit card (for free tier)
5. You get **$200 free credits** for 30 days

### Step 1.2: Create Cosmos DB Resource
1. Go to Azure Portal: https://portal.azure.com
2. Click "Create a resource"
3. Search for "Azure Cosmos DB"
4. Click "Azure Cosmos DB" → Create
5. Configure:
   ```
   Resource Group: bytemecarbon (create new)
   Account Name: bytemecarbon-<your-name>
   API: Core (SQL)
   Capacity Mode: Provisioned throughput (or Serverless for low traffic)
   Region: Pick closest to you
   Geo-Redundancy: Disable (for dev/testing)
   ```
6. Click "Review + Create" → Create
7. Wait 5-10 minutes for deployment

### Step 1.3: Get Connection String
1. Go to your Cosmos DB resource
2. Left sidebar → "Keys"
3. Copy the **Primary Connection String** (looks like):
   ```
   AccountEndpoint=https://bytemecarbon-xyz.documents.azure.com:443/;AccountKey=abc123...==;
   ```

---

## Part 2: Set Environment Variable

### Step 2.1: Windows (CMD)
```bash
setx COSMOS_CONNECTION_STRING "AccountEndpoint=https://bytemecarbon-xyz.documents.azure.com:443/;AccountKey=abc123...=="
```
Close terminal and reopen to apply.

### Step 2.2: Windows (PowerShell)
```powershell
[Environment]::SetEnvironmentVariable("COSMOS_CONNECTION_STRING", "AccountEndpoint=https://...", "User")
```

### Step 2.3: Windows (.env file - Alternative)
Create file: `ByteMeCarbon/.env`
```
COSMOS_CONNECTION_STRING=AccountEndpoint=https://bytemecarbon-xyz.documents.azure.com:443/;AccountKey=abc123...==;
```

Then in your Python code:
```python
from dotenv import load_dotenv
load_dotenv()
connection_string = os.getenv("COSMOS_CONNECTION_STRING")
```

### Step 2.4: Docker/.env (for deployment)
Create `.env` file in project root - Docker Compose will auto-load it.

---

## Part 3: Update Python Code

### Step 3.1: Update requirements.txt

**Location:** `ByteMeCarbon/requirements.txt`

**Add these lines:**
```
Flask==3.1.2
flask-cors==6.0.1
gunicorn==25.1.0
waitress==3.0.0
pytest==7.4.3
pytest-cov==4.1.0
codecarbon==3.2.2
azure-cosmos==4.5.1
python-dotenv==1.0.0
```

**Install:**
```bash
pip install -r requirements.txt
```

---

### Step 3.2: Create New File: cosmos_client.py

**Location:** `ByteMeCarbon/cosmos_client.py`

**Full Code:**
```python
"""
Azure Cosmos DB client for ByteMeCarbon.

Manages connection to Cosmos DB and provides methods for storing/retrieving optimizations.
"""

import os
from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey
from azure.core.exceptions import CosmosResourceNotFoundError
import logging

logger = logging.getLogger(__name__)

# Configuration
COSMOS_ENDPOINT = None
COSMOS_KEY = None
COSMOS_DATABASE = "bytemecarbon"
COSMOS_CONTAINER = "optimizations"

# Global client (singleton)
_cosmos_client = None
_database = None
_container = None


def init_cosmos_db():
    """
    Initialize Cosmos DB connection.
    
    Called once at app startup.
    
    Returns:
        bool: True if successful, False otherwise
    """
    global _cosmos_client, _database, _container
    
    connection_string = os.getenv("COSMOS_CONNECTION_STRING")
    
    if not connection_string:
        logger.warning("COSMOS_CONNECTION_STRING not set. Cosmos DB disabled.")
        return False
    
    try:
        _cosmos_client = CosmosClient.from_connection_string(connection_string)
        
        # Create database if doesn't exist
        try:
            _database = _cosmos_client.get_database_client(COSMOS_DATABASE)
        except CosmosResourceNotFoundError:
            _database = _cosmos_client.create_database(COSMOS_DATABASE)
            logger.info(f"Created database: {COSMOS_DATABASE}")
        
        # Create container if doesn't exist
        try:
            _container = _database.get_container_client(COSMOS_CONTAINER)
        except CosmosResourceNotFoundError:
            _container = _database.create_container(
                id=COSMOS_CONTAINER,
                partition_key=PartitionKey(path="/userId"),
                offer_throughput=400  # Minimum for Cosmos DB
            )
            logger.info(f"Created container: {COSMOS_CONTAINER}")
        
        logger.info("✅ Cosmos DB initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Cosmos DB: {str(e)}")
        return False


def store_optimization(user_id, original_code, optimized_code, metrics, filename):
    """
    Store optimization result in Cosmos DB.
    
    Args:
        user_id (str): User identifier (IP address or user account)
        original_code (str): Original Python code
        optimized_code (str): Optimized Python code
        metrics (dict): Report with complexity, performance, energy metrics
        filename (str): Original filename
        
    Returns:
        dict: Stored document with ID, or None if storage failed
    """
    if not _container:
        logger.warning("Cosmos DB not initialized")
        return None
    
    try:
        import uuid
        
        document = {
            "id": str(uuid.uuid4()),
            "userId": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "filename": filename,
            "originalCode": original_code[:5000],  # Limit size
            "optimizedCode": optimized_code[:5000],
            "metrics": metrics,
            "codeLength": {
                "before": len(original_code),
                "after": len(optimized_code)
            }
        }
        
        result = _container.create_item(body=document)
        logger.info(f"Stored optimization: {document['id']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to store optimization: {str(e)}")
        return None


def get_user_history(user_id, limit=10):
    """
    Retrieve optimization history for a user.
    
    Args:
        user_id (str): User identifier
        limit (int): Max number of records to return
        
    Returns:
        list: List of optimization records, newest first
    """
    if not _container:
        logger.warning("Cosmos DB not initialized")
        return []
    
    try:
        query = """
            SELECT * FROM c 
            WHERE c.userId = @userId 
            ORDER BY c.timestamp DESC
        """
        
        items = list(_container.query_items(
            query=query,
            parameters=[{"name": "@userId", "value": user_id}],
            max_item_count=limit
        ))
        
        logger.info(f"Retrieved {len(items)} records for user {user_id}")
        return items
        
    except Exception as e:
        logger.error(f"Failed to retrieve history: {str(e)}")
        return []


def get_optimization(item_id, user_id):
    """
    Retrieve a specific optimization by ID.
    
    Args:
        item_id (str): Optimization ID
        user_id (str): User ID (for partition key)
        
    Returns:
        dict: Optimization record, or None if not found
    """
    if not _container:
        logger.warning("Cosmos DB not initialized")
        return None
    
    try:
        item = _container.read_item(item=item_id, partition_key=user_id)
        return item
        
    except CosmosResourceNotFoundError:
        logger.warning(f"Optimization not found: {item_id}")
        return None
    except Exception as e:
        logger.error(f"Failed to retrieve optimization: {str(e)}")
        return None


def delete_optimization(item_id, user_id):
    """
    Delete an optimization record.
    
    Args:
        item_id (str): Optimization ID
        user_id (str): User ID (for partition key)
        
    Returns:
        bool: True if deleted, False otherwise
    """
    if not _container:
        logger.warning("Cosmos DB not initialized")
        return False
    
    try:
        _container.delete_item(item=item_id, partition_key=user_id)
        logger.info(f"Deleted optimization: {item_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete optimization: {str(e)}")
        return False


def get_stats():
    """
    Get Cosmos DB statistics.
    
    Returns:
        dict: Stats about container usage
    """
    if not _container:
        return {"status": "Cosmos DB not initialized"}
    
    try:
        properties = _container.read()
        return {
            "status": "Connected",
            "database": COSMOS_DATABASE,
            "container": COSMOS_CONTAINER,
            "partitionKey": "/userId",
            "lastModified": properties.get("_ts")
        }
    except Exception as e:
        return {"status": "Error", "error": str(e)}
```

---

### Step 3.3: Update app.py

**Location:** `ByteMeCarbon/app.py`

**Add imports at top (after existing imports):**
```python
from cosmos_client import init_cosmos_db, store_optimization, get_user_history
```

**Add initialization (after `app = Flask(__name__)`):**
```python
app = Flask(__name__)
CORS(app)

# Initialize Cosmos DB (optional - gracefully handles if not configured)
cosmos_enabled = init_cosmos_db()
```

**Update the upload_file function - ADD THIS inside the try block, after generating report:**

Find this section in `app.py` (around line 145):
```python
@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        # ...existing validation code...
        
        # Optimization code here...
        optimized_code_str = generate_code(optimized_ast)
        
        # Generate report
        report = generate_report(
            original_code,
            optimized_code_str,
            complexity_before,
            complexity_after,
            ...
        )
```

**ADD after the report is generated:**
```python
        # Store in Cosmos DB (if enabled)
        if cosmos_enabled:
            user_id = request.remote_addr  # Use client IP as user ID
            store_optimization(
                user_id=user_id,
                original_code=validated_code,
                optimized_code=optimized_code_str,
                metrics=report,
                filename=secure_filename(file.filename)
            )
```

**Add new route for history (add at end, before error handlers):**
```python
@app.route("/api/history", methods=["GET"])
def get_history():
    """Retrieve user's optimization history from Cosmos DB"""
    if not cosmos_enabled:
        return jsonify({"error": "Cosmos DB not enabled"}), 503
    
    user_id = request.args.get('user_id', request.remote_addr)
    limit = request.args.get('limit', 10, type=int)
    
    history = get_user_history(user_id, limit=limit)
    return jsonify({"data": history, "count": len(history)}), 200
```

---

### Step 3.4: (OPTIONAL) Update index.html

**Location:** `ByteMeCarbon/templates/index.html`

**Add this button after the reset button:**
```html
<button class="text-link" id="history-btn" style="display: none;">
    📊 View History
</button>
```

**Add this section in the HTML (after results):**
```html
<!-- History Modal -->
<div id="history-modal" class="hidden" style="
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
">
    <div style="
        background: #05070a;
        border: 1px solid rgba(0,255,136,0.3);
        border-radius: 12px;
        padding: 2rem;
        max-width: 80%;
        max-height: 80%;
        overflow-y: auto;
    ">
        <h2 style="color: #00ff88; margin-top: 0;">Your Optimization History</h2>
        <div id="history-list"></div>
        <button class="text-link" onclick="closeHistory()">Close</button>
    </div>
</div>
```

**Add JavaScript (in script.js, after existing functions):**
```javascript
// Cosmos DB History functions
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const result = await response.json();
        
        if (result.data) {
            displayHistory(result.data);
            document.getElementById('history-modal').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayHistory(items) {
    const list = document.getElementById('history-list');
    list.innerHTML = items.map(item => `
        <div style="
            border: 1px solid rgba(0,255,136,0.2);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        ">
            <p><strong>${item.filename}</strong></p>
            <p>📅 ${new Date(item.timestamp).toLocaleString()}</p>
            <p>Original: ${item.codeLength.before} bytes → Optimized: ${item.codeLength.after} bytes</p>
            <button onclick="showOptimizationDetail('${item.id}')" class="text-link">View Details</button>
        </div>
    `).join('');
}

function closeHistory() {
    document.getElementById('history-modal').classList.add('hidden');
}

// Show history button if Cosmos DB enabled
document.getElementById('history-btn')?.addEventListener('click', loadHistory);
```

---

## Part 4: Test the Connection

### Step 4.1: Test Cosmos DB Connection
```bash
python -c "
from cosmos_client import init_cosmos_db, get_stats
init_cosmos_db()
print(get_stats())
"
```

**Expected output:**
```
{
    'status': 'Connected',
    'database': 'bytemecarbon',
    'container': 'optimizations',
    'partitionKey': '/userId'
}
```

### Step 4.2: Upload a File
1. Start the app: `python app.py`
2. Open http://localhost:5000
3. Upload a Python file
4. Check Azure Portal → Your Cosmos DB → Data Explorer
5. You should see your optimization record!

### Step 4.3: Test History API
```bash
curl "http://localhost:5000/api/history?user_id=test_user&limit=5"
```

---

## Part 5: Deployment

### Docker (Recommended)

**Update Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV COSMOS_CONNECTION_STRING=${COSMOS_CONNECTION_STRING}
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

**Run with environment variable:**
```bash
docker run -e COSMOS_CONNECTION_STRING="..." -p 5000:5000 bytemecarbon
```

---

## Part 6: Troubleshooting

### Error: "COSMOS_CONNECTION_STRING not set"
✅ **Solution:** Set environment variable
```bash
setx COSMOS_CONNECTION_STRING "your_connection_string"
# Restart terminal
```

### Error: "AuthorizationPermissionDenied"
✅ **Solution:** Check connection string is correct
- Copy from Azure Portal → Keys
- Make sure no extra spaces

### Error: "CosmosResourceNotFoundError"
✅ **Solution:** Container creation failed
- Check database & container exist in Azure Portal
- Or let the code auto-create them (it will)

### Cosmos DB costs?
✅ **Solution:** Use free tier:
- First 1000 RU/s free
- 25 GB storage free
- No cost for small projects

---

## Part 7: API Reference

### Store Optimization
```python
from cosmos_client import store_optimization

store_optimization(
    user_id="192.168.1.1",
    original_code="x = 1 + 2",
    optimized_code="x = 3",
    metrics={"complexity": "O(1)"...},
    filename="test.py"
)
```

### Get User History
```python
from cosmos_client import get_user_history

history = get_user_history(user_id="192.168.1.1", limit=10)
for item in history:
    print(item['filename'], item['timestamp'])
```

### Get Single Optimization
```python
from cosmos_client import get_optimization

opt = get_optimization(item_id="abc123", user_id="192.168.1.1")
print(opt['originalCode'])
```

---

## Summary

✅ You now have:
- Azure Cosmos DB for persistent storage
- Multi-user support without collisions
- User optimization history
- Web API for data retrieval
- Optional UI for viewing history

**Next Steps:**
1. Set up Cosmos DB account (Part 1)
2. Get connection string (Part 1.3)
3. Set environment variable (Part 2)
4. Add code to app.py (Part 3)
5. Test with a file upload (Part 4)
6. Deploy to cloud (Part 5)

---

**Questions?** Check Azure Cosmos DB docs: https://learn.microsoft.com/en-us/azure/cosmos-db/
