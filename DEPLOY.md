# Deployment Checklist

## Environment Variables
Set these in Railway/Render dashboard (never commit to git):
- OPENAI_API_KEY
- HF_HOME=/app/hf_cache
- QDRANT_URL (see Qdrant Cloud section below)
- QDRANT_API_KEY (if using Qdrant Cloud)

## Switching to Qdrant Cloud
1. Create a free cluster at cloud.qdrant.io
2. Copy the cluster URL and API key
3. Set QDRANT_URL=https://<your-cluster>.cloud.qdrant.io
4. Set QDRANT_API_KEY=<your-key>
5. Update backend/qdrant_client.py get_qdrant_client() to pass
   api_key=settings.qdrant_api_key when QDRANT_API_KEY is set:
   QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
6. Re-run ingestion against the cloud cluster to populate collections

## Linking to Vercel Frontend
1. Deploy backend to Railway or Render, get the public URL
2. In Vercel project settings → Environment Variables:
   VITE_API_URL=https://<your-backend-url>
3. Redeploy the frontend — all fetch() calls use import.meta.env.VITE_API_URL

## Local Production Test
docker compose -f docker-compose.prod.yml up --build
Then verify: curl http://localhost:8000/eval
