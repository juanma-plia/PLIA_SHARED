# PLIA Shared

Shared core logic for Plia microservices.

## Installation

Install directly from GitHub:

pip install git+https://github.com/juanma-plia/PLIA_SHARED.gitOr specify a version:

pip install git+https://github.com/juanma-plia/PLIA_SHARED.git@v1.0.0## Usage

from plia_shared.database import FirestoreService
from plia_shared.core import ACLService, validate_api_key
from plia_shared.models import Serie, Character

# Initialize Firestore
firestore = FirestoreService()

# Use ACL
acl = ACLService(firestore)## Features

- 🔐 Authentication & Authorization
- 🔥 Firestore Integration with retry logic
- 📦 Shared Pydantic models
- ⚡ Async/await optimized
