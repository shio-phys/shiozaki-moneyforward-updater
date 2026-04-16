#!/bin/bash
set -e

PROJECT=shiozaki-moneyforward-updater
REGION=asia-northeast1
IMAGE=asia-northeast1-docker.pkg.dev/${PROJECT}/moneyforward-updater/moneyforward-updater:latest
JOB=moneyforward-updater

echo "=== Building image ==="
docker build --platform linux/amd64 -t "${IMAGE}" .

echo "=== Pushing image ==="
docker push "${IMAGE}"

echo "=== Updating Cloud Run Job ==="
gcloud run jobs update "${JOB}" \
  --region="${REGION}" \
  --project="${PROJECT}" \
  --image="${IMAGE}"

echo "=== Done ==="
