#!/bin/bash

set -e

case "$1" in
    uvicorn)
        uvicorn app.main:app --host 0.0.0.0 --port 8000
        ;;
    upgrade)
        # Entrypoint used for upgrades in Kubernetes
        echo "Run upgrade commands"
        alembic upgrade head
        ;;
esac
