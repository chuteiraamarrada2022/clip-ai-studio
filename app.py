from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import subprocess, shutil, uuid, json, math, re

app=FastAPI(title="Clip AI Studio v3")
BASE=Path(__file__).parent
WORK=BASE/"work"; WORK.mkdir(exist_ok=True)
app.mount("/files",StaticFiles(directory=WORK),name="files")

@app.get("/")
def home(): return FileResponse(BASE/"index.html")

def probe(path):
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],capture_output=True,text=True,check=True)
    return float(p.stdout.strip())

@app.get("/health")
def health(): return {"ok":True}

@app.post("/api/generate")
async def generate(file:UploadFile=File(...),duration:int=Form(30),topic:str=Form("conteúdo")):
    duration=max(10,min(duration,60))
    jobid=str(uuid.uuid4()); job=WORK/jobid; job.mkdir()
    src=job/"source.mp4"
    with src.open("wb") as w: shutil.copyfileobj(file.file,w)
    try: total=probe(src)
    except FileNotFoundError: raise HTTPException(500,"FFmpeg/ffprobe não instalado no servidor.")
    except Exception as e: raise HTTPException(400,"Não foi possível ler o vídeo.")
    if total < 12: raise HTTPException(400,"O vídeo precisa ter pelo menos 12 segundos.")
    clipdur=min(duration,max(10,int(total/8))) if total < duration*8 else duration
    maxstart=max(0,total-clipdur)
    starts=[(maxstart*i/7 if maxstart else 0) for i in range(8)]
    safe=re.sub(r'[^A-Za-zÀ-ÿ0-9 ]','',topic).strip() or "Conteúdo"
    titles=["O ponto que muda tudo","O que quase ninguém percebe","Entenda isso rapidamente","O erro mais comum","A explicação que faltava","Antes de continuar, veja isso","Por que isso acontece?","A ideia que vale lembrar"]
    results=[]
    for i,start in enumerate(starts):
        out=job/f"short_{i+1:02}.mp4"
        vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        cmd=["ffmpeg","-y","-ss",str(start),"-i",str(src),"-t",str(clipdur),"-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","160k","-movflags","+faststart",str(out)]
        try: subprocess.run(cmd,check=True,capture_output=True)
        except subprocess.CalledProcessError as e: raise HTTPException(500,"Falha no render FFmpeg: "+e.stderr.decode(errors="ignore")[-600:])
        meta={"title":f"{titles[i]} | {safe}","description":f"Um recorte direto sobre {safe}. #Shorts","hashtags":["#Shorts","#"+safe.replace(" ","")],"tags":[safe,"shorts"]}
        (job/f"short_{i+1:02}.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
        results.append({"id":i+1,**meta,"download":f"/files/{jobid}/{out.name}"})
    return {"job":jobid,"clips":results}
