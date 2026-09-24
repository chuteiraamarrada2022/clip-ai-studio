# Clip AI Studio v3 — deploy online

Esta versão possui backend real com FastAPI + FFmpeg e gera 8 MP4s verticais a partir de um vídeo enviado pelo usuário.

## Deploy recomendado: Render
1. Crie um repositório GitHub e envie todos os arquivos desta pasta.
2. No Render, crie um novo Web Service apontando para o repositório.
3. O Dockerfile instala FFmpeg automaticamente.
4. Depois do deploy, o Render fornece uma URL pública.
5. Abra a URL, envie um vídeo autorizado e teste.

## Local
docker build -t clip-ai .
docker run -p 8000:8000 clip-ai

Depois abra http://localhost:8000

## Limitações desta build
- Renderiza 8 cortes reais em 9:16.
- Os timestamps são distribuídos pelo vídeo, ainda não escolhidos semanticamente.
- Metadata é gerada por templates locais.
- Whisper/WhisperX + LLM ainda precisam ser conectados para transcrição, seleção inteligente, legendas sincronizadas e metadata baseada no conteúdo.
- Para produção, use object storage (S3/R2), fila de jobs e limpeza automática de arquivos.

Use somente conteúdo próprio, licenciado ou autorizado.
